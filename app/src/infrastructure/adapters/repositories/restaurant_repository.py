from datetime import datetime
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.exceptions import CityNotFoundError, RestaurantNotFoundError
from src.application.interfaces.repositories.restaurant_repository import (
    IRestaurantRepository,
)
from src.infrastructure.drivers.db.tables import City, Restaurant
from src.domain.dto.restaurant_dto import (
    AddRestaurantRequest,
    AddRestaurantResponse,
    DayShortName,
    DeleteRestaurantResponse,
    GetRestaurantsResponse,
    HoursItem,
    RestaurantActionEnum,
    RestaurantData,
    RestaurantItem,
    UpdateRestaurantRequest,
    WorkingHoursModel,
)


class RestaurantRepository(IRestaurantRepository):
    DAY_MAP = {
        0: DayShortName.MONDAY,
        1: DayShortName.TUESDAY,
        2: DayShortName.WEDNESDAY,
        3: DayShortName.THURSDAY,
        4: DayShortName.FRIDAY,
        5: DayShortName.SATURDAY,
        6: DayShortName.SUNDAY,
    }

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_restaurants_by_city_id(self, city_id: int) -> GetRestaurantsResponse:
        get_city_query = select(City).where(City.id == city_id)
        get_city_result = await self._session.execute(get_city_query)
        city = get_city_result.scalar()

        response = GetRestaurantsResponse()

        if not city:
            raise CityNotFoundError(id=city_id)

        response.data = RestaurantData(restaurants=[], center_coords=[])

        if city.latitude and city.longitude:
            response.data.center_coords = [float(city.latitude), float(city.longitude)]

        rest_query = (
            select(Restaurant)
            .where(
                Restaurant.city_id == city_id,
                Restaurant.is_active == True,
                or_(
                    Restaurant.latitude.is_not(None), Restaurant.longitude.is_not(None)
                ),
            )
            .options(
                selectinload(Restaurant.working_hours),
                selectinload(Restaurant.features),
            )
        )
        rest_result = await self._session.execute(rest_query)
        restaurants = rest_result.scalars().all()

        if not restaurants:
            raise RestaurantNotFoundError

        for rest in restaurants:
            working_hours = {}

            for wh in rest.working_hours:
                if wh.day_of_week not in self.DAY_MAP:
                    continue

                day_key = self.DAY_MAP[wh.day_of_week]
                working_hours[day_key] = HoursItem(
                    from_=wh.opens_at.strftime("%H:%M"),
                    to=wh.closes_at.strftime("%H:%M"),
                )

            # Формируем фичи
            features = [f.name for f in rest.features]

            # Добавляем ресторан в ответ
            response.data.restaurants.append(
                RestaurantItem(
                    id=rest.id,
                    address=rest.address,
                    phone=rest.phone.e164,
                    coords=[float(rest.latitude), float(rest.longitude)],
                    working_hours=WorkingHoursModel(root=working_hours),
                    features=features,
                    actions=self._get_allowed_actions(rest),
                )
            )

        return response

    async def change_restaurant_by_id(
        self, restaurant_id: int, update_restaurant: UpdateRestaurantRequest
    ) -> AddRestaurantResponse:
        restaurant = await self._session.get(Restaurant, restaurant_id)
        if not restaurant:
            raise RestaurantNotFoundError

        # Обновляем только переданные поля
        update_dict = update_restaurant.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(restaurant, key, value)

        await self._session.flush()

        # Возвращаем обновленный ресторан
        return AddRestaurantResponse(
            id=restaurant.id,
            name=restaurant.name,
            phone=restaurant.phone,
            address=restaurant.address,
            coords=[restaurant.latitude, restaurant.longitude],
            actions=self._get_allowed_actions(restaurant),
            is_active=restaurant.is_active,
        )

    async def add_restaurant_to_city_by_id(
        self, city_id: int, restaurant: AddRestaurantRequest
    ) -> AddRestaurantResponse:
        city = await self._session.get(City, city_id)
        if not city:
            raise CityNotFoundError(id=city_id)

        # Создание объекта ресторана
        new_restaurant = Restaurant(
            city_id=city_id,
            name=restaurant.name,
            phone=restaurant.phone,
            address=restaurant.address,
            latitude=restaurant.latitude,
            longitude=restaurant.longitude,
            has_delivery=restaurant.has_delivery,
            has_takeaway=restaurant.has_takeaway,
            has_dine_in=restaurant.has_dine_in,
            is_active=restaurant.is_active,
        )

        # Сохранение в БД
        self._session.add(new_restaurant)
        await self._session.flush()

        # Формирование ответа
        return AddRestaurantResponse(
            id=new_restaurant.id,
            name=new_restaurant.name,
            phone=new_restaurant.phone,
            address=new_restaurant.address,
            coords=[new_restaurant.latitude, new_restaurant.longitude],
            actions=self._get_allowed_actions(new_restaurant),
            is_active=new_restaurant.is_active,
        )

    async def delete_restaurant_by_id(
        self, restaurant_id: int
    ) -> DeleteRestaurantResponse:
        restaurant = await self._session.get(Restaurant, restaurant_id)
        if not restaurant:
            raise RestaurantNotFoundError

        await self._session.delete(restaurant)
        await self._session.flush()
        return DeleteRestaurantResponse(id=restaurant_id, message="success")

    def _get_allowed_actions(restaurant_obj: Restaurant):
        # Формирование списка доступных действий выдачи заказа
        actions = []
        if restaurant_obj.has_delivery:
            actions.append(RestaurantActionEnum.DELIVERY)
        if restaurant_obj.has_takeaway:
            actions.append(RestaurantActionEnum.TAKEAWAY)
        if restaurant_obj.has_dine_in:
            actions.append(RestaurantActionEnum.INSIDE)

        return actions

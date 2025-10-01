from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import logger
from src.infrastructure.exceptions import CityNotFoundError, RestaurantNotFoundError
from src.application.interfaces.repositories.restaurant_repository import (
    IRestaurantRepository,
)
from src.infrastructure.drivers.db.tables import City, Feature, MenuCategory, Order, Restaurant, User, WorkingHours
from src.domain.dto.restaurant_dto import (
    AddRestaurantRequest,
    AddRestaurantResponse,
    DayShortName,
    DeleteRestaurantResponse,
    GetCityRestaurantsResponse,
    GetRestaurantResponse,
    HoursItem,
    RestaurantActionEnum,
    RestaurantData,
    RestaurantItem,
    UpdateRestaurantRequest,
    UpdateRestaurantResponse,
    WorkingHoursModel,
)


class RestaurantRepository(IRestaurantRepository): # TODO: add exceptions. Response DTOs перенести в interactors
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

    async def get_restaurant_by_id(self, restaurant_id: int) -> Restaurant:
        stmt = (
            select(Restaurant)
            .where(Restaurant.id == restaurant_id)
            .options(
                selectinload(Restaurant.working_hours),
                selectinload(Restaurant.features),
            )
        )
        result = await self._session.execute(stmt)
        restaurant = result.scalar_one_or_none()

        if not restaurant:
            raise RestaurantNotFoundError(id=restaurant_id)

        return restaurant


    async def get_restaurant_by_last_user_order(self, user_id: int) -> Optional[Restaurant]:
        stmt = (
            select(Restaurant)
            .join(
                Order,
                Restaurant.id == Order.restaurant_id
            )
            .join(
                User,
                Order.user_id == User.id
            )
            .where(User.id == user_id)
            .order_by(
                Order.id.desc() # Latest order
            )
            .limit(1)
        )
        result = await self._session.execute(stmt)
        restaurant = result.scalars().first()
        
        return restaurant


    async def get_city_restaurants(self, city: City) -> GetCityRestaurantsResponse:
        response = GetCityRestaurantsResponse()
        response.data = RestaurantData(restaurants=[], center_coords=[])

        if city.latitude and city.longitude:
            response.data.center_coords = [float(city.latitude), float(city.longitude)]

        rest_query = (
            select(Restaurant)
            .where(
                Restaurant.city_id == city.id,
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
            # Добавляем ресторан в ответ
            response.data.restaurants.append(
                RestaurantItem(
                    id=rest.id,
                    name=rest.name,
                    address=rest.address,
                    phone=rest.phone.e164,
                    coords=[float(rest.latitude), float(rest.longitude)],
                    working_hours=WorkingHoursModel(root=self._get_working_hours(rest)),
                    features=self._get_features(rest),
                    actions=self._get_allowed_actions(rest),
                )
            )

        return response

    async def update_restaurant(
        self, restaurant: Restaurant, update_restaurant: UpdateRestaurantRequest
    ) -> UpdateRestaurantResponse:
        # Обновляем только переданные поля
        update_dict = update_restaurant.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if key not in ["working_hours", "features"]:
                setattr(restaurant, key, value)

        # Обновляем часы работы, если они переданы
        if update_restaurant.working_hours is not None:
            # Создаем словарь существующих часов работы для быстрого доступа
            existing_hours = {wh.day_of_week: wh for wh in restaurant.working_hours}
            
            for day, hours in update_restaurant.working_hours.root.items():
                day_of_week = next(k for k, v in self.DAY_MAP.items() if v == day)
                
                # Если часы для этого дня уже существуют - обновляем
                if day_of_week in existing_hours:
                    wh = existing_hours[day_of_week]
                    wh.opens_at = datetime.strptime(hours.from_, "%H:%M").time()
                    wh.closes_at = datetime.strptime(hours.to, "%H:%M").time()
                    wh.is_holiday = hours.is_holiday
                else:
                    # Иначе создаем новые
                    new_wh = WorkingHours(
                        restaurant_id=restaurant.id,
                        day_of_week=day_of_week,
                        opens_at=datetime.strptime(hours.from_, "%H:%M").time(),
                        closes_at=datetime.strptime(hours.to, "%H:%M").time(),
                        is_holiday=hours.is_holiday
                    )
                    self._session.add(new_wh)

        # Обновляем фичи, если они переданы
        if update_restaurant.features is not None:
            # Очищаем текущие фичи
            restaurant.features.clear()

            # Находим и добавляем новые фичи
            stmt = select(Feature).where(Feature.name.in_(update_restaurant.features)) # TODO: вынести в отдельны репозиторий
            result = await self._session.execute(stmt)
            features = result.scalars().all()
            restaurant.features.extend(features)

        # Обновляем категории меню, если они переданы
        if update_restaurant.menu_categories is not None:
            # Очищаем текущие категории меню
            restaurant.menu_categories.clear()

            # Находим и добавляем новые категории меню
            stmt = select(MenuCategory).where(MenuCategory.id.in_(update_restaurant.menu_categories)) # TODO: вынести в отдельный репозиторий
            result = await self._session.execute(stmt)
            menu_categories = result.scalars().all()
            restaurant.menu_categories.extend(menu_categories)

        await self._session.flush()

        # Возвращаем обновленный ресторан
        return UpdateRestaurantResponse(
            id=restaurant.id,
            name=restaurant.name,
            phone=restaurant.phone.e164,
            address=restaurant.address,
            coords=[restaurant.latitude, restaurant.longitude],
            is_active=restaurant.is_active,
            working_hours=WorkingHoursModel(root=self._get_working_hours(restaurant)),
            features=self._get_features(restaurant),
            menu_categories=self._get_menu_categories(restaurant),
            actions=self._get_allowed_actions(restaurant),
        )

    async def add_restaurant_to_city_by_id(
        self, city: City, restaurant: AddRestaurantRequest
    ) -> AddRestaurantResponse:
        # Создание объекта ресторана
        new_restaurant = Restaurant(
            city_id=city.id,
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
        self._session.add(new_restaurant)
        await self._session.flush()
        
        working_hours_list: List[WorkingHours] = []
        for day_num in range(7):
            working_hours = WorkingHours(
                restaurant_id=new_restaurant.id,
                day_of_week=day_num,
                opens_at=datetime.strptime("09:00", "%H:%M").time(),
                closes_at=datetime.strptime("22:00", "%H:%M").time(),
                is_holiday=True
            )
            self._session.add(working_hours)
            working_hours_list.append(working_hours)
        
        await self._session.flush()

        # Формируем working_hours вручную, не вызывая _get_working_hours
        working_hours_model = {}
        for wh in working_hours_list:
            day_key = self.DAY_MAP[wh.day_of_week]
            working_hours_model[day_key] = HoursItem(
                from_=wh.opens_at.strftime("%H:%M"),
                to=wh.closes_at.strftime("%H:%M"),
                is_holiday=wh.is_holiday,
            )

        # Формирование ответа
        return AddRestaurantResponse(
            id=new_restaurant.id,
            name=new_restaurant.name,
            phone=new_restaurant.phone,
            address=new_restaurant.address,
            coords=[new_restaurant.latitude, new_restaurant.longitude],
            is_active=new_restaurant.is_active,
            actions=self._get_allowed_actions(new_restaurant),
            working_hours=WorkingHoursModel(root=working_hours_model),
            menu_categories=[],
            features=[],
        )


    async def delete_restaurant(
        self, restaurant: Restaurant
    ) -> DeleteRestaurantResponse:
        await self._session.delete(restaurant)
        await self._session.flush()
        return DeleteRestaurantResponse(id=restaurant.id, message="success")

    def _get_allowed_actions(self, restaurant_obj: Restaurant):
        # Формирование списка доступных действий выдачи заказа
        actions = []
        if restaurant_obj.has_delivery:
            actions.append(RestaurantActionEnum.DELIVERY)
        if restaurant_obj.has_takeaway:
            actions.append(RestaurantActionEnum.TAKEAWAY)
        if restaurant_obj.has_dine_in:
            actions.append(RestaurantActionEnum.INSIDE)

        return actions

    def _get_working_hours(self, restaurant_obj: Restaurant):
        working_hours = {}

        for wh in restaurant_obj.working_hours:
            if wh.day_of_week not in self.DAY_MAP:
                continue

            day_key = self.DAY_MAP[wh.day_of_week]
            working_hours[day_key] = HoursItem(
                from_=wh.opens_at.strftime("%H:%M"),
                to=wh.closes_at.strftime("%H:%M"),
                is_holiday=wh.is_holiday,
            )

        return working_hours

    def _get_features(self, restaurant_obj: Restaurant):
        features = []

        for feature in restaurant_obj.features:
            features.append(feature.name)

        return features

    def _get_menu_categories(self, restaurant_obj: Restaurant):
        menu_categories = []

        for menu_category in restaurant_obj.menu_categories:
            menu_categories.append(menu_category.id)

        return menu_categories

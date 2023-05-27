import csv
import random
import string

from geopy import distance
from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    create_engine,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from app.settings import settings

engine = create_engine(settings.database_url)
Session = sessionmaker(bind=engine)
session = Session()

metadata = MetaData()


Base = declarative_base(metadata=metadata)


class Location(Base):
    __tablename__ = "locations"

    zip = Column(String, primary_key=True)
    lat = Column(Float)
    lng = Column(Float)
    city = Column(String)
    state_name = Column(String)

    @staticmethod
    def load_locations_to_db():
        data = []
        with open("app/uszips.csv", "r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                existing_location = (
                    session.query(Location).filter_by(zip=row["zip"]).first()
                )
                if existing_location:
                    continue
                location = Location(
                    zip=row["zip"],
                    lat=row["lat"],
                    lng=row["lng"],
                    city=row["city"],
                    state_name=row["state_name"],
                )
                data.append(location)
        return data


class Cargo(Base):
    __tablename__ = "cargos"

    id = Column(Integer, primary_key=True)
    pick_up_location_id = Column(String, ForeignKey("locations.zip"))
    delivery_location_id = Column(String, ForeignKey("locations.zip"))
    weight = Column(Float)
    description = Column(String)

    pick_up_location = relationship(Location, foreign_keys=[pick_up_location_id])
    delivery_location = relationship(Location, foreign_keys=[delivery_location_id])

    def calculate_distance(self):
        if self.pick_up_location and self.delivery_location:
            pick_up_coords = (self.pick_up_location.lat, self.pick_up_location.lng)
            delivery_coords = (self.delivery_location.lat, self.delivery_location.lng)
            dist = distance.distance(pick_up_coords, delivery_coords).miles
            return dist
        return None


class Truck(Base):
    __tablename__ = "trucks"

    id = Column(Integer, primary_key=True)
    name = Column(String, default="DAF Trucks")
    truck_number = Column(String)
    current_location_id = Column(String, ForeignKey("locations.zip"))
    carrying_capacity = Column(Float)

    current_location = relationship(Location, foreign_keys=[current_location_id])

    @staticmethod
    def get_random_location():
        query = session.query(Location).order_by(func.random()).first()
        return query.zip if query else None

    @staticmethod
    def generate_unique_number():
        number = random.randint(1000, 9999)
        letter = random.choice(string.ascii_uppercase)
        unique_number = f"{number}{letter}"
        return unique_number

    @classmethod
    def create_default_trucks(cls, num_trucks):
        default_trucks = []
        for _ in range(num_trucks):
            random_location = cls.get_random_location()
            truck = cls(
                truck_number=cls.generate_unique_number(),
                current_location_id=random_location,
                carrying_capacity=random.randint(1, 1000),
            )
            default_trucks.append(truck)
        return default_trucks


async def create_tables():
    Base.metadata.create_all(engine)

    # Загрузка данных в таблицу locations
    data = Location.load_locations_to_db()
    session.add_all(data)
    session.commit()

    # Создание случайных значений current_location_id в таблице trucks
    default_trucks = Truck.create_default_trucks(20)
    session.add_all(default_trucks)
    session.commit()

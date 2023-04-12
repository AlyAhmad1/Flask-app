"""Database class and methods"""

import configparser
import os

import sqlalchemy as db
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

cfg = configparser.ConfigParser()
cfg.read('configuration.ini')


# Database class that is used to connect with DB.
class Database:
    """DB class that use to connect with different methods"""
    # engine = db.create_engine(
    #     'postgresql://' + cfg['Database']['user'] + ':' +
    #     cfg['Database']['password'] + '@' + cfg['Database'][
    #         'host'] + '/' + cfg['Database']['name'])

    engine = db.create_engine(
        'sqlite://' + '/' + 'temp_DB.db')

    def __init__(self):
        self.connection = self.engine.connect()
        self.session = Session(bind=self.connection)
        print("DB Instance created")

    # fetch on record ( hotel ) against hotel_id
    def fetch_hotel_by_id(self, hotel_id):
        """ fetch hotel data by id"""
        fetch_query = self.session.query(Hotel). \
            filter(Hotel.id == hotel_id).first()
        return fetch_query

    # fetch on record ( hotel ) against market_id
    def fetch_hotel_by_market_id(self, market_id):
        """ fetch hotel data by market id"""
        fetch_query = self.session.query(Hotel). \
            filter(Hotel.item_market_id == market_id).first()

        return fetch_query

    # return records ( Matched Hotel data )
    def fetch_hotel_by_match(self, match):
        """ fetch all hotel data"""
        fetch_query = self.session.query(Hotel). \
            filter(Hotel.item_match == match).all()
        return fetch_query

    # return all hotels data
    def fetch_all_hotels(self):
        """ fetch all hotel data"""
        hotels = self.session.query(Hotel).all()
        return hotels

    # add record in Hotel (model )
    def add_hotel(self, hotel):
        """ all hotel to DB"""
        self.session.add(hotel)
        self.session.commit()

    # Update record in Hotel (model )
    def update_hotel(self, hotel_id, market_id, name, url, address):
        """ update hotel data"""
        data_to_update = {Hotel.item_market_id: market_id,
                          Hotel.item_name: name, Hotel.item_url: url,
                          Hotel.item_address: address}
        hotel_data = self.session.query(Hotel).filter(Hotel.id == hotel_id)
        hotel_data.update(data_to_update)
        self.session.commit()

    def update_scrapped_hotel(self, scraper_id, description,
                              rating, day, time, match):
        """ update hotel data"""
        data_to_update = {Hotel.item_description: description,
                          Hotel.item_rating: rating,
                          Hotel.item_last_update: day + " at " + time,
                          Hotel.item_match: match}
        hotel_data = self.session.query(Hotel).filter(Hotel.id == scraper_id)
        hotel_data.update(data_to_update)
        self.session.commit()

    # delete record from ( Hotel data )
    def delete_hotel(self, hotel_id):
        """ delete hotel data"""
        hotel_data = self.session.query(Hotel). \
            filter(Hotel.id == hotel_id).first()
        self.session.delete(hotel_data)
        self.session.commit()

    # Fetch all records from Image model
    def fetch_all_images(self, hotel_id):
        """ fetch all image data"""
        images = self.session.query(Images). \
            filter(Images.item_hotel == hotel_id).all()
        return images

    # Fetch all records from Schedule ( Model )
    def fetch_all_schedules(self, hotel_id, day, time):
        """ fetch all schedule data"""
        if day == '' and time == '':
            schedules = self.session.query(Schedules). \
                filter(Schedules.item_hotel == hotel_id).all()
        elif hotel_id == '':
            schedules = self.session.query(Schedules). \
                filter(Schedules.schedule_day == day).filter(
                Schedules.schedule_time == time).all()
        else:
            schedules = self.session.query(Schedules). \
                filter(Schedules.item_hotel == hotel_id). \
                filter(Schedules.schedule_day == day). \
                filter(Schedules.schedule_time == time).all()

        return schedules

    # Fetch record from Schedule ( Model )
    def fetch_schedule_by_id(self, schedule_id):
        """ fetch schedule data by id"""
        fetch_query = self.session.query(Schedules). \
            filter(Schedules.id == schedule_id).first()

        return fetch_query

    # add new record in Schedule ( Model )
    def add_schedule(self, schedule):
        """ add schedule data """
        self.session.add(schedule)
        self.session.commit()

    # delete record from Schedule ( Model )
    def delete_schedule(self, schedule_id):
        """ delete schedule data """
        schedules_data = self.session.query(Schedules). \
            filter(Schedules.id == schedule_id).first()
        self.session.delete(schedules_data)

        self.session.commit()

    # delete multiple record in Schedule ( Model )
    def delete_schedules(self, hotel_id):
        """ delete schedules data"""
        schedules_data = self.session.query(Schedules). \
            filter(Schedules.item_hotel == hotel_id)
        for schedule in schedules_data:
            self.session.delete(schedule)
        self.session.commit()

    # Update all record in Schedule for specific hotel id's ( Model )
    def update_all_schedule(self, run_status):
        """ update schedule data """
        data_to_update = {Schedules.run: run_status}
        schedules_data = self.session.query(Schedules). \
            filter(Schedules.item_hotel > 0)
        schedules_data.update(data_to_update)

    def update_hotel_scrapper_fail(self, scrapper_id, day, time):
        """ Run when scrapper fails"""
        data_to_update = {Hotel.item_last_update: day + " at " + time}
        hotel_data = self.session.query(Hotel). \
            filter(Hotel.id == scrapper_id)
        hotel_data.update(data_to_update)

        data_to_update = {Schedules.run: 'F'}
        schedules_data = self.session.query(Schedules). \
            filter(Schedules.item_hotel == id). \
            filter(Schedules.schedule_day == day).filter(Schedules.schedule_time == time)
        schedules_data.update(data_to_update)

        self.session.commit()

    # Fetch record from Schedule against status of schedule ( Model )
    def fetch_schedule_by_run(self, run_status):
        """ detch schedule data """
        fetch_query = self.session.query(Schedules). \
            filter(Schedules.run == run_status).all()
        return fetch_query

    # add record in Image model
    def add_image(self, image):
        """ add image data """
        self.session.add(image)
        self.session.commit()

    # update record in Image model
    def update_image(self, hotel_id, url, hash_data):
        """ update image data """
        data_to_update = {Images.item_url: url, Images.item_hash: hash_data}
        images_data = self.session.query(Images). \
            filter(Images.item_hotel == hotel_id)
        images_data.update(data_to_update)
        self.session.commit()

    # Update record in Schedule ( Model )
    def update_schedule(self, item_hotel, day, time, run_status):
        """ update schedule data """
        data_to_update = {Schedules.run: run_status}
        schedules_data = self.session.query(Schedules). \
            filter(Schedules.item_hotel == item_hotel).filter(
            Schedules.schedule_day == day).filter(Schedules.schedule_time == time)
        schedules_data.update(data_to_update)
        self.session.commit()

    # delete record from Image model
    def delete_images(self, hotel_id):
        """ delete image data """
        images_data = self.session.query(Images). \
            filter(Images.item_hotel == hotel_id).all()
        for image in images_data:
            self.session.delete(image)
            self.session.commit()
        try:
            os.rmdir(f"static/images/{id}")
            print("Directory '% s' has been removed successfully")
        except OSError as error:
            print(error)
            print(f"Directory /images{id} can not be removed")


# DB base class that is used to create new models
Base = declarative_base()


# Hotel Model
class Hotel(Base):
    """Model for hotel account."""
    __tablename__ = 'hotels'
    item_name = Column(String)
    item_url = Column(String)
    item_description = Column(String)
    item_rating = Column(String)
    item_market_id = Column(String)
    item_address = Column(String)
    item_last_update = Column(String)
    item_match = Column(Boolean)
    id = Column(Integer, primary_key=True)


class Images(Base):
    # item_hotel, item_url,item_hash
    """Model for images account."""
    __tablename__ = 'images'
    item_hotel = Column(Integer)
    item_url = Column(String)
    item_hash = Column(String)
    id = Column(Integer, primary_key=True)


class Schedules(Base):
    # item_hotel,schedule_day,schedule_time,run
    """Model for Schedules account."""
    __tablename__ = 'schedules'
    item_hotel = Column(Integer)
    schedule_day = Column(String)
    schedule_time = Column(String)
    run = Column(String)
    id = Column(Integer, primary_key=True)


Base.metadata.create_all(bind=Database.engine)

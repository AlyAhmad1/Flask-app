"""app.py is main file which contains end-points of route"""

from flask import jsonify, flash

from config import db, messages
from database import Hotel, Schedules


# return data of a hotel against market_id
def query_hotel_endpoint(**kwargs):
    """
        This function run by GET request.
        parameter:
        market_id (str): string variable
        returns:
         data of hotel against this market_id.
         if data not found then returns an error message ( NOt Found )
    """
    market_id = kwargs["market_id"]
    hotel = db.fetch_hotel_by_market_id(market_id)
    if hotel is None:
        return jsonify({'error': messages["api.get_hotel"]["not_found"]})
    images = []
    images_data = db.fetch_all_images(hotel.id)
    if images_data is not None:
        for image in images_data:
            images.append(image.item_url)

    schedules = []
    schedules_data = db.fetch_all_schedules(hotel.id, '', '')
    for schedule in schedules_data:
        schedules.append(schedule.schedule_day +
                         " at " + schedule.schedule_time)

    return jsonify(
        {'id': hotel.id, 'name': hotel.item_name,
         'item_url': hotel.item_url, 'description': hotel.item_description,
         'rating': hotel.item_rating, 'market_id': hotel.item_market_id,
         'address': hotel.item_address,
         'last_update': hotel.item_last_update,
         'images': images, 'schedules': schedules})


# create a new record in Hotel Model and return its data
def create_hotel_api_endpoint(**kwargs):
    """
        This function run by PUT request.
        parameters:
            This accepts Json Schema
            market_id (str): string variable
            name (str): string variable
            url (str): string variable
            address (str): string variable
        returns:
            Create hotel and return data of hotel.
            if data not found then returns an error message ( NOt Found )
    """
    record = kwargs["record"]
    hotel = Hotel(item_name=record["name"],
                  item_url=record["url"],
                  item_description='', item_rating='',
                  item_market_id=record["market_id"],
                  item_address=record["address"],
                  item_last_update='',
                  item_match=False)
    db.add_hotel(hotel)

    hotel = db.fetch_hotel_by_market_id(record["market_id"])
    if hotel is None:
        return jsonify({'error': messages["api.get_hotel"]["not_found"]})

    return jsonify(
        {'id': hotel.id, 'name': hotel.item_name,
         'item_url': hotel.item_url, 'description': hotel.item_description,
         'rating': hotel.item_rating, 'market_id': hotel.item_market_id,
         'address': hotel.item_address,
         'last_update': hotel.item_last_update,
         'images': [], 'schedules': []})


# delete record from Hotel Model against Market_id linked ith hotel
def delete_hotel_endpoint(**kwargs):
    """
        This function run by DELETE request.
        parameters:
            market_id (str): string variable
        returns:
            Delete data of hotel that linked ith market_id.
            if hotel data not found then returns an error message ( NOt Found )
    """
    market_id = kwargs["market_id"]
    hotel = db.fetch_hotel_by_market_id(market_id)
    if hotel is None:
        return jsonify({'error': messages["api.get_hotel"]["not_found"]})

    db.delete_hotel(hotel.id)
    db.delete_schedules(hotel.id)
    return jsonify({'info': messages["api.remove_hotel"]["success"]})


# Update record from Hotel Model against Market_id linked ith hotel
def update_hotel_endpoint(**kwargs):
    """
        This function run by POST request.
        parameters:
             market_id (str): string variable
             name (str): string variable
             url (str): string variable
             address (str): string variable
        returns:
            Update hotel and return data of hotel.
            if hotel data not found then returns an error message ( NOt Found )
    """
    record = kwargs["record"]
    hotel = db.fetch_hotel_by_market_id(record["market_id"])
    if hotel is None:
        return jsonify({'error': messages["api.get_hotel"]["not_found"]})

    db.update_hotel(
        hotel.id, record["market_id"], record["name"], record["url"], record["address"])
    hotel = db.fetch_hotel_by_market_id(record["market_id"])
    if hotel is None:
        return jsonify({'error': messages["api.modify_hotel"]["fail"]})
    return jsonify({'id': hotel.id, 'name': hotel.item_name, 'item_url': hotel.item_url,
                    'description': hotel.item_description, 'rating': hotel.item_rating,
                    'market_id': hotel.item_market_id, 'address': hotel.item_address,
                    'last_update': hotel.item_last_update, 'images': [], 'schedules': []})


# return data of Scraper against running day and time. ( mean schedule time )
def query_schedules_endpoint():
    """
        This function run by GET request.
        Parameter:
            No Parameter require for this function
        returns:
            return Scrapper data along with the time it will run on.
    """
    schedules = []
    schedules_data = db.fetch_schedule_by_run("P")
    if len(schedules_data) > 0:
        for item in schedules_data:
            hotel = db.fetch_hotel_by_id(item.item_hotel)
            schedules.append(hotel.item_name + " to run " +
                             item.schedule_day + " at " + item.schedule_time)
    return jsonify({'schedules': schedules})


# create a new schedule against hotel id on specific day and time
def create_schedule_api_endpoint(**kwargs):
    """
        This function run by PUT request.
        parameters:
             market_id (str): string variable
             day (str): string variable
             time (str): string variable
        returns:
            add a new scrapper and link with hotel (By hotel market_id).
            if hotel data not found then returns an error message ( NOt Found )
    """

    record = kwargs["record"]
    hotel = db.fetch_hotel_by_market_id(record["market_id"])
    if hotel is None:
        return jsonify({'error': messages["api.get_hotel"]["not_found"]})

    schedule = db.fetch_all_schedules(
        hotel.id, record["day"], record["time"])
    if len(schedule) == 0:
        schedule = Schedules(
            item_hotel=hotel.id, schedule_day=record["day"],
            schedule_time=record["time"], run='P')
        db.add_schedule(schedule)
    schedules_data = db.fetch_all_schedules(hotel.id, '', '')
    schedules = []
    if schedules_data:
        for item in schedules_data:
            hotel = db.fetch_hotel_by_id(item.item_hotel)
            schedules.append(
                {"id": item.id, "hotel": hotel.item_name,
                 "day": item.schedule_day, "time": item.schedule_time})

    return jsonify({'schedules': schedules})


# Show hotel data against hotel ( market_id )
def show_hotel_data(**kwargs):
    """
        show_hotel function accepts both GET and POST requests.
        GET reqeust return list hotels ,
        POST request return a single hotel data against market_id.
        both request render data on hotel.html ( template page )
        if hotel data not found then returns an error message ( NOt Found )
    """
    form = kwargs["form"]
    post_method = kwargs["post_method"]
    lst_hotel = []
    images = []
    if post_method == 1:
        market_id = form["market_id"]
        lst_hotel = db.fetch_hotel_by_market_id(market_id)
        if lst_hotel is not None:
            images = db.fetch_all_images(lst_hotel.id)
        else:
            flash(messages["hotel.show"]["fail"])
    hotels = db.fetch_all_hotels()
    return {"hotels": hotels, "lst_hotel": lst_hotel, "images": images}

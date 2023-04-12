"""api.py is main file which contains all the data of route"""

import json

from flask import flash
from flask import render_template, request, url_for, redirect, jsonify

from app import query_hotel_endpoint, create_hotel_api_endpoint, \
    delete_hotel_endpoint, update_hotel_endpoint, \
    query_schedules_endpoint, create_schedule_api_endpoint, show_hotel_data
from config import app, db, messages
from database import Hotel, Schedules
from utilities import scrape_data


# Route to get Hotel by market id
@app.route('/api/getHotelByMarketId', methods=['GET'])
def query_hotel():
    """
        This function run by GET request.
        parameter:
        market_id (str): string variable
        returns:
         data of hotel against this market_id.
    """
    market_id = request.args.get('market_id')
    return query_hotel_endpoint(market_id=market_id)


# Add hotel to list of hotels along with the Hotel id
@app.route('/api/addHotelByMarketId', methods=['PUT'])
def create_hotel_api():
    """
        This function run by PUT request.
        parameters:
            market_id (str): string variable
            name (str): string variable
            url (str): string variable
            address (str): string variable
        returns:
            Create hotel and return data of hotel.
    """
    record = json.loads(request.data)
    return create_hotel_api_endpoint(record=record)


# Remove hotel from DB ( by unique market id )
@app.route('/api/deleteHotelByMarketId', methods=['DELETE'])
def delete_hotel():
    """
        This function run by DELETE request.
        parameters:
            market_id (str): string variable
        returns:
            Delete data of hotel that linked ith market_id.
    """
    market_id = request.args.get('market_id')
    return delete_hotel_endpoint(market_id=market_id)


# Update Hotel data using market Id
@app.route('/api/updateHotelByMarketId', methods=['POST'])
def update_hotel():
    """
        This function run by POST request.
        parameters:
             market_id (str): string variable
             name (str): string variable
             url (str): string variable
             address (str): string variable
        returns:
            Update hotel and return data of hotel.
    """
    record = json.loads(request.data)
    return update_hotel_endpoint(record=record)


# this function will return all scrappers that are waiting in queue
@app.route('/api/giveMeCurrentWaitingScrappingList', methods=['GET'])
def query_schedules():
    """
        This function run by GET request.
        returns:
            return Scrapper data along with the time it will run on.
    """
    return query_schedules_endpoint()


# Add a new scheduler by marketId
@app.route('/api/addScheduleByMarketId', methods=['PUT'])
def create_schedule_api():
    """
        This function run by PUT request.
        parameters:
             market_id (str): string variable
             day (str): string variable
             time (str): string variable
        returns:
            add a new scrapper and link with hotel (By hotel market_id).
    """
    record = json.loads(request.data)
    return create_schedule_api_endpoint(record=record)


# delete scheduler from queue by marketId
@app.route('/api/deleteScheduleById', methods=['DELETE'])
def delete_schedule_api():
    """
        This function run by DELETE request.
        parameters:
             schedule_id (str): string variable
        returns:
            remove scrapper from the queue of scrapper by schedule_id.
    """
    schedule_id = request.args.get('schedule_id')
    db.delete_schedule(schedule_id)
    return jsonify({'info': messages["api.remove_schedule"]["success"]})


# home page of application that will display all hotel data stored in DB
@app.route('/')
def index():
    """
        index function run by GET request and render template index.html ( template page ).
        Display all hotel data added in DB.
    """
    hotels = db.fetch_all_hotels()
    return render_template('index.html', hotels=hotels)


# get a single hotel data by name and market-id ( POST request ) , Get all hotel data ( GET request)
@app.route('/hotel', methods=('GET', 'POST'))
def show_hotel():
    """
        show_hotel function accepts both GET and POST requests.
        GET reqeust return list hotels ,
        POST request return a single hotel data against market_id.
        both request render data on hotel.html ( template page )
    """
    form = {}
    post_method = 0
    if request.method == 'POST':
        form = request.form
        post_method = 1
    data = show_hotel_data(post_method=post_method, form=form)
    return render_template('hotel.html', hotels=data["hotels"], hotel=data["lst_hotel"],
                           images=data["images"], len=len(data["images"]))


# fetch data of specific hotel by using model-id
@app.route('/hotel/<hotel_id>', methods=('GET', 'POST'))
def hotel(hotel_id):
    """
        hotel function accepts both GET and POST requests.
        GET reqeust return list hotels ,
        POST request return a single hotel data against hotel-id.
        both request render data on hotel.html ( template page )
    """
    print("request came here")
    print("-------------")
    print("-------------")
    print("-------------")
    lst_hotel = []
    images = []
    if hotel_id != "":
        lst_hotel = db.fetch_hotel_by_market_id(hotel_id)
        images = db.fetch_all_images(lst_hotel.id)
    hotels = db.fetch_all_hotels()
    return render_template('hotel.html', hotels=hotels, hotel=lst_hotel,
                           images=images, len=len(images))


# create new hotel by ( POST request )
@app.route('/create', methods=('GET', 'POST'))
def create():
    """
        create function accepts both GET and POST requests.
        GET reqeust return list hotels ,
        POST request Create a new hotel
        parameters:
             name  (str): string variable
             url  (str): string variable
             market_id  (str): string variable
             address  (str): string variable
        both request render data on create.html ( template page )
    """
    lst_hotel = [0, "", "", "", "", "", ""]
    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        market_id = request.form["market_id"]
        address = request.form["address"]
        lst_hotel = [0, name, url, "", "", market_id, address]
        if url == "" or name == "" or market_id == "" or address == "":
            flash(messages["hotel.add"]["fail"])
        else:
            lst_hotel = Hotel(item_name=name, item_url=url,
                              item_description='', item_rating='',
                              item_market_id=market_id, item_address=address,
                              item_last_update='', item_match=False)
            db.add_hotel(lst_hotel)
            lst_hotel = db.fetch_hotel_by_market_id(market_id)
            flash(messages["hotel.add"]["success"])
            return redirect(url_for('create', id=lst_hotel.id))
    hotels = db.fetch_all_hotels()
    return render_template('create.html', hotel=lst_hotel, hotels=hotels)


# create or update hotel by market-id
@app.route('/create/<hotel_id>', methods=('GET', 'POST'))
def create_hotel(hotel_id):
    """
        create function accepts both GET and POST requests.
        GET reqeust return list hotels ,
        POST request Create a new hotel
        parameters:
             name (str): string variable
             url (str): string variable
             market_id (str): string variable
             address (str): string variable
        both request render data on create.html ( template page )
    """
    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        market_id = request.form["market_id"]
        address = request.form["address"]
        if not url:
            flash(messages["hotel.add"]["fail"])
        else:
            db.update_hotel(hotel_id, market_id, name, url, address)
            flash(messages["hotel.add"]["success"])
    lst_hotel = db.fetch_hotel_by_id(hotel_id)
    hotels = db.fetch_all_hotels()
    return render_template('create.html', hotel=lst_hotel, hotels=hotels)


@app.route('/create_schedule', methods=['GET', 'POST'])
def create_schedule():
    """
        create_schedule function accepts both GET and POST requests.
        GET request list data of all hotels
        POST request used to Create a new schedule
        parameters:
            schedule_market_id (str): string variable
            hotel (str): string variable
            date_day (str): string variable
            datetime (str): string variable
        both request render data on create_schedules.html ( template page )
    """
    lst_hotel = []
    schedules = []
    market_id = ""
    schedule_market_id = ""
    scrape_option = ["checked", ""]
    if request.method == 'POST' and \
            (request.form['schedule_market_id'] != "" or request.form['hotel'] != ""):
        if request.form['schedule_market_id'] == "":
            schedule_market_id = request.form['hotel']
        else:
            schedule_market_id = request.form['schedule_market_id']
        date_day = request.form['dateday']
        date_time = request.form['datetime']
        if not schedule_market_id or not date_day or not date_time:
            flash(messages["schedule.add"]["fail"])
        else:
            lst_hotel = db.fetch_hotel_by_market_id(schedule_market_id)
            hotel_id = lst_hotel.id
            schedule = db.fetch_all_schedules(hotel_id, date_day, date_time)
            if len(schedule) == 0:
                schedule = Schedules(
                    item_hotel=hotel_id, schedule_day=date_day, schedule_time=date_time, run='P')
                db.add_schedule(schedule)
            schedules = db.fetch_all_schedules(hotel_id, '', '')
            scrape_option = ["", "checked"]
    hotels = db.fetch_all_hotels()
    return render_template('create_schedules.html',
                           schedule_market_id=schedule_market_id,
                           market_id=market_id,
                           scrape_option=scrape_option, hotel=lst_hotel,
                           hotels=hotels, schedules=schedules)


@app.route('/create_schedule/<schedule_id>', methods=['GET', 'POST'])
def add_schedule(schedule_id):
    """
        add_schedule function accepts both GET and POST requests.
        GET request list data of all hotels
        POST request used to Create a new schedule
        parameters:
            schedule_market_id (str): string variable
            hotel (str): string variable
            date_day (str): string variable
            datetime (str): string variable
        both request render data on create_schedules.html ( template page )
    """
    lst_hotel = []
    schedules = []
    market_id = ""
    schedule_market_id = ""
    scrape_option = ["", "checked"]
    if request.method == 'POST' and request.form['schedule_market_id'] != "":
        schedule_market_id = request.form['schedule_market_id']
        date_day = request.form['dateday']
        date_time = request.form['datetime']
        if not schedule_market_id or not date_day or not date_time:
            flash(messages["schedule.add"]["fail"])
        else:
            lst_hotel = db.fetch_hotel_by_market_id(schedule_market_id)
            schedule_id = lst_hotel.id
            schedule = db.fetch_all_schedules(schedule_id, date_day, date_time)

            if len(schedule) == 0:
                schedule = Schedules(
                    item_hotel=schedule_id, schedule_day=date_day, schedule_time=date_time, run='P')
                db.add_schedule(schedule)
    if schedule_id == "":
        market_id = ""
    else:
        lst_hotel = db.fetch_hotel_by_market_id(schedule_id)
        if lst_hotel is not None:
            schedule_id = lst_hotel.id
            schedules = db.fetch_all_schedules(schedule_id, '', '')
    hotels = db.fetch_all_hotels()
    return render_template('create_schedules.html',
                           schedule_market_id=schedule_market_id,
                           market_id=market_id,
                           scrape_option=scrape_option,
                           hotel=lst_hotel, hotels=hotels, schedules=schedules)


@app.route('/modify/<hotel_id>', methods=('GET', 'POST'))
def show_edit(hotel_id):
    """
        show_edit function accepts both GET and POST requests.
        GET request return data of hotel against id ( hotel-id)
        parameters:
            id (str): string variable
        POST request used to Update hotel data
        parameters:
            Market_id (str): string variable
            hotel (str): string variable
            name (str): string variable
            url (str): string variable
            address (str): string variable
        both request render data on modify.html ( template page )
    """
    modify_id = hotel_id
    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        market_id = request.form["market_id"]
        address = request.form["address"]
        if not market_id:
            flash(messages["hotel.modify"]["fail"])
        else:
            lst_hotel = db.fetch_hotel_by_market_id(modify_id)
            hotel_id = lst_hotel.id
            db.update_hotel(hotel_id, market_id, name, url, address)
            modify_id = market_id
            flash(messages["hotel.modify"]["success"])
    hotels = db.fetch_all_hotels()
    lst_hotel = db.fetch_hotel_by_market_id(modify_id)
    return render_template('modify.html', hotel=lst_hotel, hotels=hotels)


@app.route('/modify', methods=('GET', 'POST'))
def edit():
    """
        show_edit function accepts both GET and POST requests.
        GET request return data of hotel against id ( hotel-id)
        parameters:
            id (str): string variable
        POST request used to Update hotel data
        parameters:
            Market_id (str): string variable
            hotel (str): string variable
            name (str): string variable
            url (str): string variable
            address (str): string variable
        both request render data on modify.html ( template page )
    """
    lst_hotel = []
    market_id = ""
    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        market_id = request.form["market_id"]
        address = request.form["address"]
        if not market_id:
            flash(messages["hotel.modify"]["fail"])
        else:
            lst_hotel = db.fetch_hotel_by_market_id(market_id)
            hotel_id = lst_hotel.id
            db.update_hotel(hotel_id, market_id, name, url, address)
    hotels = db.fetch_all_hotels()
    if market_id != "":
        lst_hotel = db.fetch_hotel_by_market_id(market_id)
    return render_template('modify.html', hotel=lst_hotel, hotels=hotels)


@app.route('/delete/<hotel_id>', methods=['GET', 'POST'])  #
def show_delete(hotel_id):
    """
        show_delete function accepts both GET and POST requests.
        GET request return list of hotels
        parameters:
            id (str): string variable
        POST request used to delete hotel data
        parameters:
            Market_id (str): string variable
        both request render data on remove.html ( template page )
    """
    lst_hotel = db.fetch_hotel_by_market_id(hotel_id)
    if request.method == 'POST':
        market_id = request.form["market_id"]
        lst_hotel = db.fetch_hotel_by_market_id(market_id)
        if lst_hotel is not None:
            hotel_id = lst_hotel.id
            try:
                db.delete_hotel(hotel_id)
            except ValueError as exception_value:
                print(exception_value)
            try:
                db.delete_images(hotel_id)
            except ValueError as exception_value:
                print(exception_value)
            try:
                db.delete_schedules(hotel_id)
            except ValueError as exception_value:
                print(exception_value)
            flash(messages["hotel.remove"]["success"])
        else:
            flash(messages["hotel.remove"]["fail"])
    hotels = db.fetch_all_hotels()
    return render_template('remove.html', hotel=lst_hotel, hotels=hotels)


@app.route('/delete', methods=['GET', 'POST'])  #
def delete():
    """
        show_delete function accepts both GET and POST requests.
        GET request return list of hotels
        parameters:
            id (str): string variable
        POST request used to delete hotel data
        parameters:
            Market_id (str): string variable
        both request render data on remove.html ( template page )
    """
    if request.method == 'POST':
        market_id = request.form["market_id"]
        lst_hotel = db.fetch_hotel_by_market_id(market_id)
        if lst_hotel is not None:
            hotel_id = lst_hotel.id
            try:
                db.delete_hotel(hotel_id)
            except ValueError as exception_value:
                print(exception_value)

            try:
                db.delete_images(hotel_id)
            except ValueError as exception_value:
                print(exception_value)

            try:
                db.delete_schedules(hotel_id)
            except ValueError as exception_value:
                print(exception_value)

            flash(messages["hotel.remove"]["success"])
        else:
            flash(messages["hotel.remove"]["fail"])
    else:
        lst_hotel = []
    hotels = db.fetch_all_hotels()
    return render_template('remove.html', hotel=lst_hotel, hotels=hotels)


@app.route('/clear_history/<history_id>', methods=('POST',))  #
def clear_history(history_id):
    """
        clear_history function accepts POST requests.
        POST request used to Clear History data
        parameters:
            id (str): string variable
    """
    db.update_scrapped_hotel(history_id, '', '', '', '', False)
    db.delete_images(history_id)
    flash(messages["hotel.history_clear"]["success"])
    lst_hotel = db.fetch_hotel_by_id(history_id)
    hotels = db.fetch_all_hotels()
    return render_template('remove.html', hotel=lst_hotel, hotels=hotels)


# delete Schedule from List
@app.route('/delete_schedule/<schedule_id>', methods=['POST'])  #
def delete_schedule(schedule_id):
    """
        delete_schedule function accepts POST requests.
        POST request used to delete schedule data
        parameters:
            id (str): string variable
    """
    schedule = db.fetch_schedule_by_id(schedule_id)
    lst_hotel = db.fetch_hotel_by_id(schedule.item_hotel)
    db.delete_schedule(schedule_id)
    flash(messages['schedule.remove']['success'])
    return redirect(url_for('add_schedule', id=lst_hotel.item_market_id))


# return Scrapper data against market_id
@app.route('/scrape', methods=('GET', 'POST'))
def scrape():
    """
        scrape function accepts both GET and POST requests.
        POST request used to get schedule data
        parameters:
            market_id  (str): string variable
        both request render data on create_schedules.html ( template page )
    """
    market_id = ""
    if request.method == 'POST':
        if request.form['market_id'] != "":
            try:
                market_id = request.form['market_id']
                lst_hotel = db.fetch_hotel_by_id(market_id)
                hotel_id = lst_hotel.id
                if scrape_data([hotel_id]):
                    return redirect(url_for('hotel', id=market_id))
                flash(messages["hotel.scrape"]["fail"])
            except Exception as exception_value:
                print(exception_value)

                flash(messages["hotel.scrape"]["fail"])
        else:
            flash(messages["hotel.scrape"]["fail"])
    return render_template('create_schedules.html', schedule_market_id="", market_id=market_id,
                           scrape_option=["checked", ""], hotel=[], hotels=[], schedules=[])


# Swagger Doc page all APIs endpoint documentation will appear here
@app.route('/api/docs/')
def get_docs():
    """
    swagger_ui calling method
    """
    return render_template('swaggerUi.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0')

# Item Catalog project

A server rendering page which contains a Mobile and computer accessories store. The project contains a databse to store information and a server to render web pages and diplay the database info. Project is built using python with the help of SQLAlchemy libreary (for linking to database and SQL staff) and Flask framing creator. The prjoect is secured using OAuth2 and requires users to login with their google accounts to acivate all features.

## Quick start
**Step1**: Setting up your environment. preferably, use FSND vagrant machine

#### vagrant installation
* Install virtualBox which is the software that actually runs the virtual machine from this link 
```
https://www.virtualbox.org/wiki/Download_Old_Builds_5_1 
```
* Donlowad vagrant from this link 
```
https://www.vagrantup.com/downloads.html
```
* Download VM configuration by forking repository ``` https://github.com/udacity/fullstack-nanodegree-vm```  and cloning it on your device.
* In your terminal, cd into **fullstack-nanodegree-vm** directory and you will find another directory called **vagrant**. 
* Change directory to the **vagrant** directory.
* In your terminal type command ```vagrant up``` to download the linux operating system and install it. 
* After finishing, run ```vagrant ssh``` to log into your newly installed linux vm. 


#### Code setup 
* Clone the project on your computer. 
* In your git teminal run the data_creation.py file
```
$ python data_creation.py
```
* In your git teminal run the project.py file
```
$ python project.py
```
* Open you localhost in your browser at port 5000 --> localhost:5000

##### Json endpoints: 
If you need to observe the data in a json format, you can access links as following: 
* **localhost:5000/mobily/categories/json** : Obtaining the data for all categories in accessory sections.
* **localhost:5000/mobily/-number between 1 and 6-/items/json** : Obtaining all items stored in a particular category section. 
* **localhost:5000/mobily/-number between 1 and 31 -/itemdetail/json** : obtaining all the information specified for an item in a particular category.


### Quick demo to the code files. 
* database.py file: Contains Classes used to create the databse. 
* data_creation.py file: Contains the actual data stored in the database which are (users, accessories types, accessories sections and items in each section)
* project.py file: Contains server creation code. Server contains (Frames to navigate between pages and read and process data in the database, Securing the data using OAuth2 standard)
* templates folder: The folder contain all the html files to be rendered on the browser. 
* static folder: Contains img folder which contains all rendered images and css folder which contains all the css files for styling the page. 

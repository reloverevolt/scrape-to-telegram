# scrape-to-telegram
my first pet project

THIS IS A REAL WORLD TELEGRAM BOT EXAMPLE TO BE DEPLOYED ON HEROKU

see live in telegram @bankisale

Features:

1. Daily scraping of products and updating a database (Postgres hosted on heroku).
2. Processing images of products stored on AWS S3. Basically it gets an image of a product
reconstructs the background and pastes a sale stamp on it with calculated discount.
3. Generating product offer to be posted to telegram channel according to the following structure:

Image,
PID,
Product link with refferal code inserted,
Product title,
Old and New Price,
Sentiments(like & dislike) and Interraction(see product, duscuss in chat) Keyboard

4. All of the business logic such as product brands, min sale, refferal codes, shop names are stored in google spreadsheet

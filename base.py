from flask import Flask,render_template,redirect,url_for,session
from pymongo import MongoClient
from bson.objectid import ObjectId

mongoURL="mongodb://localhost:27017"

client=MongoClient(mongoURL)
db=client.AJIO
collection_bigBrandParty=db.big_brand_party
collection_min40PercentOff=db.min40PercentOff
collection_product=db.product
collection_cart=db.cart

app=Flask(__name__)

@app.route("/")
def home():
    bigBrandParty=collection_bigBrandParty.find({})
    return render_template('main.html',bigBrandParty=bigBrandParty)

@app.route("/singup",methods=['GET','POST'])
def signup():
    return render_template('signup.html')

@app.route("/minOff/<int:newId>",methods=['GET','POST'])
def min40PercentOff(newId):
    data=collection_min40PercentOff.find({"newId":newId})
    return render_template('min40PercentOff.html',data=data)

@app.route("/product/<int:productId>",methods=['GET','POST'])
def product(productId):
    data=collection_product.find_one({"productId":productId})
    return render_template('product.html',data=data)

@app.route("/add_to_cart/<int:productId>",methods=['GET','POST'])
def add_to_cart(productId):
    # add_item=collection_cart.insert_one({"productId":productId})
    existing_item = collection_cart.find_one({"productId":productId})
    if existing_item:
        # If the item is already in the cart, redirect to the cart page
        return redirect(url_for('cart'))
    
    # Fetch the product details from the product collection
    else:
        data=collection_product.find_one({"productId": productId})
        collection_cart.insert_one(data)
    
        return redirect(url_for('cart'))    

@app.route("/cart",methods=['GET','POST'])
def cart():
    # Fetch all items from the cart collection
    cart_items = collection_cart.find({})
    
    total_sum = 0
    # Iterate over the items to calculate the total price
    for item in cart_items:
        # Ensure 'price' is numeric and handle cases where 'price' might be missing
        total_sum += item['offer'] * item['quantity'] # Use 0 as the default value if 'offer' is not found
    
    # Re-fetch items to pass them to the template
    cart_items = collection_cart.find({})
    
    # Render the cart page with the cart items and the calculated sum
    return render_template('cart.html', data=cart_items, sum=total_sum)

@app.route("/inc_quantity/<int:productId>",methods=['GET','POST'])
def inc_quantity(productId):
    cart_item=collection_cart.find_one({"productId":productId})
    new_quantity=cart_item['quantity']+1
    collection_cart.update_one({"productId": productId},{"$set": {"quantity": new_quantity}})
    cart_item=collection_cart.find_one({"productId":productId})
    return redirect(url_for('cart'))

@app.route("/dec_quantity/<int:productId>",methods=['GET','POST'])
def dec_quantity(productId):
    cart_item=collection_cart.find_one({"productId":productId})
    if cart_item['quantity']==1:
        return redirect(url_for('cart'))
    else:
        new_quantity=cart_item['quantity']-1
        collection_cart.update_one({"productId": productId},{"$set": {"quantity": new_quantity}})
    cart_item=collection_cart.find_one({"productId":productId})
    return redirect(url_for('cart'))
    



if __name__== '__main__':
    app.run(debug=True, port=5001)
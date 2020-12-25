from django.http import request
from django.shortcuts import render, HttpResponse
from .models import *
from django.views import View
from django.shortcuts import redirect
from django.contrib.auth.hashers import make_password, check_password
# Create your views here.



class Home(View):
    def get(self, request):
        products = Product.objects.all()
        cats = Category.objects.all()
        args = {'products':products, 'cats':cats}
        return render(self.request, 'Store/index.html', args)
    
    def post(self, request):
        product = request.POST.get('product')
        cart = request.session.get('cart')
        remove = request.POST.get('remove')

        if cart:
            quantity = cart.get(product)

            if quantity:
                if remove:
                    cart[product] = quantity - 1
                else:
                    cart[product] = quantity + 1
            else:
                cart[product] = 1
            if cart[product] < 1:
                cart.pop(product)
        else:
            cart = {}
            cart[product] = 1
        request.session['cart'] = cart

        return redirect('home')


class Cart(View):
    def map_function(self, product):
        cart = self.request.session.get('cart', None)
        product_id = str(product.id)

        if product_id in cart:
            if product.discount_price:
                return product.price * cart[product_id]
            else:

                return product.price * cart[product_id]



    def get(self, request):
        ids = list(request.session.get('cart').Keys)
        cart_products = Product.get_products_id(ids)
        product_prices = list(map(self.map_function, cart_products))
        total = sum(product_prices)
        args = {'cart_products':cart_products, 'total':total}
        return render(self.request, 'Home/cart.html', args)


class Checkout(View):
    def post(self, request):
        fname = request.POST.get('fname')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        cart = request.session.get('cart')
        customer = request.session.get('customer')
        products = Product.get_products_id(list(cart.keys()))

        for product in products:
            # order = Order(customer=Customer(id=customer['id']), product=product, fname=fname,
            #               price=product.price, phone=phone, address=address, quantity=cart.get(str(product.id)))
            ## IF Product has Discount Price This method must be called

            if product.discount_price:
                order = Order(customer=Customer(id=customer['id']), product=product, fname=fname, price=product.discount_price, phone=phone, address=address, quantity=cart.get(str(product.id)))
            else:
                order = Order(customer=Customer(id=customer['id']), product=product, fname=fname,
                          price=product.price, phone=phone, address=address, quantity=cart.get(str(product.id)))



            order.save()

        request.session['cart'] = {}

        return redirect('user_orders')
        

class Search(View):
    def get(self, request):
        query = request.GET['query']
        products = Product.objects.filter(name__icontains=query)
        args = {'products': products}
        return render(self.request, 'Home/search.html', args)

class Register(View):
    def get(self, request):
        return render(request, 'signupsignin/signup.html')

    def post(self, request):
        try:
            postData = request.POST
            phone_number = postData.get('phone_number')
            email = postData.get('email')
            password = postData.get('password')
            print(phone_number, email, password)
            customer = Customer(phone_number=phone_number,
                                email=email, password=password)
            customer.password = make_password(customer.password)
            customer.register()
    
            args = {}
            return redirect('login')
        except:
            return HttpResponse("Email Or Phone Number Already Exists Please Try again")

class Login(View):
    def get(self, request):
        return render(request, 'signupsignin/signin.html')

    def post(self, request):
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        customer = Customer.get_customer(phone_number)
        error_message = None
        if customer:
            match = check_password(password, customer.password)
            if match:
                customer.__dict__.pop('_state')
                request.session['customer'] = customer.__dict__
                return redirect('Home')
            else:
                error_message = 'Phone number or Password didnt match on our record'
        else:
            error_message = 'No Customer Found! Please Registrer First!'
        print(phone_number, password)
        context = {'error_message': error_message}
        return render(request, 'signupsignin/signin.html', context)



def logout(request):
    request.session.clear()
    return redirect('Home')



class UserOrders(View):
    def map_func(self, product):
        cart = self.request.session.get('cart', None)
        product_id = str(product.id)

        if product_id in cart:
            if not product.disc_price:
                
                return product.price * cart[product_id]
            else:
                return product.disc_price * cart[product_id] 
    
    def get(self, request):
        customer = request.session.get('customer')
        user_orders = Order.get_orders_by_customer(customer)
        print(user_orders)
        args = {'user_orders': user_orders}
        return render(self.request, 'Home/all_orders.html', args)    




## Payment View 
#         
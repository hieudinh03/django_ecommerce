from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.http import HttpResponseRedirect,HttpResponse
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from .models import Cart, CartItem, Product
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
def home_view(request):
    products = models.Product.objects.all()
    if request.user.is_authenticated:
        cart = models.Cart.objects.filter(user=request.user).first()
        product_count_in_cart = cart.items.count() if cart else 0
        return HttpResponseRedirect('afterlogin')
    else:
        product_count_in_cart = 0
    return render(request, 'ecom/index.html', {'products': products, 'product_count_in_cart': product_count_in_cart})

 
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


def customer_signup_view(request):
    userForm=forms.CustomerUserForm()
    customerForm=forms.CustomerForm()
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST)
        customerForm=forms.CustomerForm(request.POST,request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customer=customerForm.save(commit=False)
            customer.user=user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
        return HttpResponseRedirect('customerlogin')
    return render(request,'ecom/customersignup.html',context=mydict)

def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()


def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    else:
        return redirect('admin-dashboard')

@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    # for cards on dashboard
    customercount=models.Customer.objects.all().count()
    productcount=models.Product.objects.all().count()
    ordercount=models.Orders.objects.all().count()

    # for recent order tables
    orders=models.Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_by=models.Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)

    mydict={
    'customercount':customercount,
    'productcount':productcount,
    'ordercount':ordercount,
    'data':zip(ordered_products,ordered_bys,orders),
    }
    return render(request,'ecom/admin_dashboard.html',context=mydict)


# admin view customer table
@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers=models.Customer.objects.all()
    return render(request,'ecom/view_customer.html',{'customers':customers})

# admin delete customer
@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')


@login_required(login_url='adminlogin')
def update_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('view-customer')
    return render(request,'ecom/admin_update_customer.html',context=mydict)

# admin view the product
@login_required(login_url='adminlogin')
def admin_products_view(request):
    products=models.Product.objects.all()
    return render(request,'ecom/admin_products.html',{'products':products})


# admin add product by clicking on floating button
@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    productForm=forms.ProductForm()
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
        return HttpResponseRedirect('admin-products')
    return render(request,'ecom/admin_add_products.html',{'productForm':productForm})


@login_required(login_url='adminlogin')
def delete_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')


@login_required(login_url='adminlogin')
def update_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    productForm=forms.ProductForm(instance=product)
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST,request.FILES,instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')
    return render(request,'ecom/admin_update_product.html',{'productForm':productForm})


@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    orders=models.Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_by=models.Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)
    return render(request,'ecom/admin_view_booking.html',{'data':zip(ordered_products,ordered_bys,orders)})


@login_required(login_url='adminlogin')
def delete_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')

# for changing status of order (pending,delivered...)
@login_required(login_url='adminlogin')
def update_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    orderForm=forms.OrderForm(instance=order)
    if request.method=='POST':
        orderForm=forms.OrderForm(request.POST,instance=order)
        if orderForm.is_valid():
            orderForm.save()
            return redirect('admin-view-booking')
    return render(request,'ecom/update_order.html',{'orderForm':orderForm})


# admin view the feedback
@login_required(login_url='adminlogin')
def view_feedback_view(request):
    feedbacks=models.Feedback.objects.all().order_by('-id')
    return render(request,'ecom/view_feedback.html',{'feedbacks':feedbacks})



def search_view(request):
    query = request.GET.get('query', '')
    products = models.Product.objects.filter(name__icontains=query)

    if request.user.is_authenticated:
        cart = models.Cart.objects.filter(user=request.user).first()
        if cart:
            product_count_in_cart = cart.items.count()
        else:
            product_count_in_cart = 0
    else:
        product_count_in_cart = 0

    word = "Searched Result :"

    if request.user.is_authenticated:
        return render(request, 'ecom/customer_home.html',
                      {'products': products, 'word': word, 'product_count_in_cart': product_count_in_cart})
    else:
        return render(request, 'ecom/index.html',
                      {'products': products, 'word': word, 'product_count_in_cart': product_count_in_cart})



@login_required(login_url='customerlogin')
def add_to_cart_view(request, pk):
    product = models.Product.objects.get(id=pk)
    cart, created = models.Cart.objects.get_or_create(user=request.user)
    cart_item, created = models.CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()
    else:
        cart_item.quantity = 1
        cart_item.save()

    messages.info(request, f'{product.name} added to cart successfully!')
    return redirect('customer-home')


# for checkout of cart

def cart_view(request):
    if request.user.is_authenticated:
        cart = models.Cart.objects.filter(user=request.user).first()
        if cart:
            items = cart.items.all()
            total = sum(item.subtotal() for item in items)
        else:
            items = []
            total = 0
    else:
        items = []
        total = 0

    return render(request, 'ecom/cart.html', {'items': items, 'total': total})


def update_cart_quantity(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        quantity_change = int(request.POST.get('quantity_change'))

        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)

        cart_item.quantity += quantity_change
        if cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()

        total = sum(item.product.price * item.quantity for item in CartItem.objects.filter(cart=cart))

        return JsonResponse({
            'status': 'success',
            'total': total,
            'quantity': cart_item.quantity,
            'subtotal': cart_item.quantity * cart_item.product.price
        })
    return JsonResponse({'status': 'error'}, status=400)

@login_required(login_url='customerlogin')
def remove_from_cart_view(request, pk):
    if request.user.is_authenticated:
        cart = models.Cart.objects.filter(user=request.user).first()
        if cart:
            try:
                cart_item = models.CartItem.objects.get(cart=cart, product_id=pk)
                cart_item.delete()
                messages.info(request, 'Product removed from cart.')
            except models.CartItem.DoesNotExist:
                messages.error(request, 'Product not found in cart.')
        else:
            messages.error(request, 'No cart found for user.')
    else:
        messages.error(request, 'User not authenticated.')

    return redirect('cart_view')


def send_feedback_view(request):
    feedbackForm=forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'ecom/feedback_sent.html')
    return render(request, 'ecom/send_feedback.html', {'feedbackForm':feedbackForm})



@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_home_view(request):
    products = models.Product.objects.all()

    if request.user.is_authenticated:
  
        cart = models.Cart.objects.filter(user=request.user).first()
        if cart:
       
            cart_items = cart.items.all()
            product_count_in_cart = len(set(item.product.id for item in cart_items))
        else:
            product_count_in_cart = 0
    else:
        product_count_in_cart = 0 

    return render(request, 'ecom/customer_home.html', {
        'products': products,
        'product_count_in_cart': product_count_in_cart
    })



# shipment address before placing order
@login_required(login_url='customerlogin')
def customer_address_view(request):
    product_in_cart = request.user.is_authenticated and models.Cart.objects.filter(user=request.user).exists()

    if request.user.is_authenticated:
        cart = models.Cart.objects.get(user=request.user)
        product_count_in_cart = cart.items.count()
    else:
        product_count_in_cart = 0

    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            email = addressForm.cleaned_data['Email']
            mobile = addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']
            total = 0
            if request.user.is_authenticated:
                cart = models.Cart.objects.get(user=request.user)
                products = cart.items.all()
                for item in products:
                    total += item.product.price * item.quantity

            response = render(request, 'ecom/payment.html', {'total': total})
            response.set_cookie('email', email)
            response.set_cookie('mobile', mobile)
            response.set_cookie('address', address)
            return response
    return render(request, 'ecom/customer_address.html', {'addressForm': addressForm, 'product_in_cart': product_in_cart, 'product_count_in_cart': product_count_in_cart})




@login_required(login_url='customerlogin')
def payment_success_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    products = None
    email = request.COOKIES.get('email', None)
    mobile = request.COOKIES.get('mobile', None)
    address = request.COOKIES.get('address', None)

    if request.user.is_authenticated:
        cart = models.Cart.objects.get(user=request.user)
        items = cart.items.all()
        for item in items:
            models.Orders.objects.get_or_create(
                customer=customer,
                product=item.product,
                status='Pending',
                email=email,
                mobile=mobile,
                address=address
            )
        cart.items.all().delete()

    response = render(request, 'ecom/payment_success.html')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response




@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_order_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    orders=models.Orders.objects.all().filter(customer_id = customer)
    ordered_products=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_products.append(ordered_product)

    return render(request,'ecom/my_order.html',{'data':zip(ordered_products,orders)})




import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def download_invoice_view(request,orderID,productID):
    order=models.Orders.objects.get(id=orderID)
    product=models.Product.objects.get(id=productID)
    mydict={
        'orderDate':order.order_date,
        'customerName':request.user,
        'customerEmail':order.email,
        'customerMobile':order.mobile,
        'shipmentAddress':order.address,
        'orderStatus':order.status,

        'productName':product.name,
        'productImage':product.product_image,
        'productPrice':product.price,
        'productDescription':product.description,


    }
    return render_to_pdf('ecom/download_invoice.html',mydict)






@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'ecom/my_profile.html',{'customer':customer})


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return HttpResponseRedirect('my-profile')
    return render(request,'ecom/edit_profile.html',context=mydict)



def aboutus_view(request):
    return render(request,'ecom/aboutus.html')

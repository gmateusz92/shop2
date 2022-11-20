from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, OrderItem, Order
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm

def item_list(request):
    items = Item.objects.all()
    return render(request, 'home-page.html', {'items': items})

class CheckoutView(View):
    def get(self, *args, **kwargs):
        # form
        form = CheckoutForm()
        return render(self.request, 'checkout-page.html', {'form':form})
    def post(self, *args, **kwargs):
        if form.is_valid():
            print('the form is valid')
            return redirect('app:checkout-page')


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = 'home-page.html'

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return render(self.request, 'order_summary.html', {'order': order})
        except ObjectDoesNotExist:
            messages.error(self.request, 'You do not have an active order')
            return redirect('/')






class ItemDetailView(DetailView): #dla detail dajemy object w templates
    model = Item
    template_name = 'product-page.html'


@login_required()
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create( #created bo zwraca tuple
        item=item,
        user=request.user,
        ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)# jezeli uzytkownik ma juz zamowienia ale nie ukonczone
    if order_qs.exists(): #jezeli query set istnieje
        order = order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "this item quantity was updated")
        else:
            messages.info(request, "this item was added to your card")
            order.items.add(order_item)
            return redirect('app:order-summary')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item) #skad items
        messages.info(request, "this item was added to your card")
    return redirect('app:order-summary')


@login_required()
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists(): #jezeli query set istnieje
        order = order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "this item was removed from  your card")
            return redirect('app:order-summary')
        else:
            #add a message saying the user doesnt have an order
            messages.info(request, "this item was not in your card")
    else:
        messages.info(request, "ypu do not have an active order")
        return redirect('app:product-page', slug=slug)
    return redirect('app:product-page', slug=slug)

@login_required()
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists(): #jezeli query set istnieje
        order = order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "this item quantity was updated")
            return redirect('app:order-summary')
        else:
            #add a message saying the user doesnt have an order
            messages.info(request, "this item was not in your card")
    else:
        messages.info(request, "ypu do not have an active order")
        return redirect('app:product-page', slug=slug)
    return redirect('app:product-page', slug=slug)
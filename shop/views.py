import json
import logging

from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from cart.forms import CartAddProductForm
from orders.models import OrderItem

from .forms import NewsletterSignupForm
from .models import Category, NewsletterSubscriber, Product


logger = logging.getLogger(__name__)

def product_list(request, category_slug=None):
    category=None
    categories=Category.objects.all()
    products=Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products=products.filter(category=category)
    featured_products = products.order_by('-created')[:3]
    new_arrivals = products.order_by('-created')[:6]
    bestsellers = (
        products
        .annotate(purchases=Count('order_items'))
        .order_by('-purchases', '-created')[:6]
    )
    category_highlights = (
        categories
        .annotate(product_total=Count('products'))
        .order_by('-product_total')[:6]
    )
    newsletter_form = NewsletterSignupForm()
    if request.method == "POST" and request.POST.get("form_type") == "newsletter":
        newsletter_form = NewsletterSignupForm(request.POST)
        if newsletter_form.is_valid():
            email = newsletter_form.cleaned_data["email"]
            subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
            if created:
                messages.success(request, "Thanks for joining the list! Expect fresh drops soon.")
            else:
                messages.info(request, "You're already on the list—stay tuned for new arrivals.")
            return redirect('shop:product_list')
        else:
            messages.error(request, "Please provide a valid email address to subscribe.")

    hero_slides = [
        {
            "eyebrow": "New Season · Capsule 2026",
            "title": "Everyday essentials, elevated.",
            "description": "Discover tactile finishes, grounded palettes, and thoughtful craftsmanship.",
            "tagline": "Week 04 drop · 320 units worldwide",
            "primary_cta": {"label": "Shop new arrivals", "href": f"{reverse('shop:product_search')}?q=new"},
            "secondary_cta": {"label": "View cart", "href": reverse('cart:cart_detail')},
            "image": "https://images.unsplash.com/photo-1503602642458-232111445657?auto=format&fit=crop&w=1600&q=80",
            "accent": "#38bdf8",
        },
        {
            "eyebrow": "Makers we love",
            "title": "Small batch, big feeling.",
            "description": "Limited ceramics, hand-loomed throws, and accents with a story.",
            "tagline": "Hand-thrown in Limuru · Signed editions",
            "primary_cta": {"label": "Meet the artisans", "href": "#"},
            "secondary_cta": {"label": "Gift guide", "href": "#"},
            "image": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1600&q=80",
            "accent": "#f97316",
        },
        {
            "eyebrow": "Studio playlists",
            "title": "Soundtrack your rituals.",
            "description": "Weekly playlists curated to match each collection's mood.",
            "tagline": "Updated every Friday · 52 min",
            "primary_cta": {"label": "Listen now", "href": "#"},
            "secondary_cta": {"label": "Follow on Spotify", "href": "https://spotify.com"},
            "image": "https://images.unsplash.com/photo-1483412033650-1015ddeb83d1?auto=format&fit=crop&w=1600&q=80",
            "accent": "#a855f7",
        }
    ]
    hero_slider_interval = 6000
    hero_slider_autoplay = True
    hero_slider_pause_on_interaction = True

    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'bestsellers': bestsellers,
        'category_highlights': category_highlights,
        'newsletter_form': newsletter_form,
        'hero_slides': hero_slides,
        'hero_slider_interval': hero_slider_interval,
        'hero_slider_autoplay': hero_slider_autoplay,
        'hero_slider_pause_on_interaction': hero_slider_pause_on_interaction,
    }

    return render(request, 'shop/product/list.html', context)

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()

    # Related products (same category, excluding current product)
    related_products = (
        Product.objects.filter(category=product.category, available=True)
        .exclude(id=product.id)[:4]
    )

    # Frequently bought together
    order_items = OrderItem.objects.filter(product=product)
    product_ids = (
        OrderItem.objects
        .filter(order__in=[item.order for item in order_items])
        .exclude(product=product)
        .values('product')
        .annotate(count=Count('product'))
        .order_by('-count')[:4]
    )
    frequently_bought = Product.objects.filter(id__in=[p['product'] for p in product_ids])

    return render(
        request,
        'shop/product/detail.html',
        {
            'product': product,
            'cart_product_form': cart_product_form,
            'related_products': related_products,
            'frequently_bought': frequently_bought,
        },
    )

def product_search(request):
    query = request.GET.get('q')
    results= []

    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query), available=True)

    return render(request,
                  'shop/product_search.html',
                  {'query': query,
                   'results': results})


@csrf_exempt
@require_POST
def telemetry_event(request):
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'invalid_json'}, status=400)

    event_name = payload.get('event') or 'unknown'
    metrics = payload.get('metrics', {})
    meta = {
        'event': event_name,
        'metrics': metrics,
        'path': payload.get('path') or request.META.get('HTTP_REFERER'),
        'ts': payload.get('ts'),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'user': request.user.id if request.user.is_authenticated else None,
    }

    logger.info('telemetry_event', extra={'telemetry': meta})

    return JsonResponse({'ok': True})
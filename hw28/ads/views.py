import json

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from ads.models import Category, Ad
from avito import settings
from users.models import User


def index(request):

    return JsonResponse({"status": "ok"})


class CategoryListView(ListView):
    model = Category

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        response = []
        for category in self.object_list.order_by("name"):
            response.append({
                "id": category.id,
                "name": category.name
            })

        return JsonResponse(response, safe=False)


class CategoryDetailView(DetailView):
    model = Category

    def get(self, request, *args, **kwargs):
        category = self.get_object()

        return JsonResponse({
            "id": category.id,
            "name": category.name,
        })


@method_decorator(csrf_exempt, name='dispatch')
class CategoryCreateView(CreateView):
    model = Category
    fields = ["name"]

    def post(self, request, *args, **kwargs):
        json_data = json.loads(request.body)

        category = Category.objects.create(name=json_data["name"])

        return JsonResponse({
            "id": category.id,
            "name": category.name,
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryUpdateView(UpdateView):
    model = Category
    fields = ["name"]

    def put(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        json_data = json.loads(request.body)

        self.object.name = json_data["name"]
        self.object.save()

        return JsonResponse({
            "id": self.object.id,
            "name": self.object.name,
        })


@method_decorator(csrf_exempt, name='dispatch')
class CategoryDeleteView(DeleteView):
    model = Category
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"status": "ok"}, status=204)


@method_decorator(csrf_exempt, name='dispatch')
class AdListView(ListView):
    model = Ad

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        paginator = Paginator(self.object_list.select_related("user").order_by("-price"), settings.TOTAL_ON_PAGE)
        page_number = int(request.GET.get("page", 1))
        page_obj = paginator.get_page(page_number)

        ad_list = []
        for ad in page_obj:
            ad_list.append({
                "id": ad.id,
                "name": ad.name,
                "price": ad.price,
                "description": ad.description,
                "is_published": ad.is_published,
                "category_id": ad.category_id,
                "user_id": ad.user_id,
                "username": ad.user.username,
                "image": ad.image.url if ad.image else None,
            })

        response = {
            "items": ad_list,
            "total": paginator.count,
            "num_pages": paginator.num_pages,
        }
        return JsonResponse(response, safe=False)


class AdDetailView(DetailView):
    model = Ad

    def get(self, request, *args, **kwargs):
        ad = self.get_object()

        return JsonResponse({
            "id": ad.id,
            "name": ad.name,
            "price": ad.price,
            "description": ad.description,
            "is_published": ad.is_published,
            "category_id": ad.category_id,
            "user_id": ad.user_id,
            "image": ad.image.url if ad.image else None,
        })


@method_decorator(csrf_exempt, name='dispatch')
class AdCreateView(CreateView):
    model = Ad
    fields = ["name", "price", "description", "category", "user"]

    def post(self, request, *args, **kwargs):
        json_data = json.loads(request.body)

        user_obj = get_object_or_404(User, pk=json_data["user_id"])  # Попытка достать юзера по id
        # Если пользователя нет, то запись не будет создана
        ad = Ad.objects.create(
            name=json_data["name"],
            price=json_data["price"],
            description=json_data["description"],
        )

        ad.category, _ = Category.objects.get_or_create(name=json_data["category"])  # Назначаем категорию,
        # либо создаем новую, если ее нет

        ad.user = user_obj

        ad.save()

        return JsonResponse({
            "id": ad.id,
            "name": ad.name,
            "price": ad.price,
            "description": ad.description,
            "is_published": ad.is_published,
            "category_id": ad.category_id,
            "user_id": ad.user_id,
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class AdUpdateView(UpdateView):
    model = Ad
    fields = ["name", "price", "description", "is_published", "category"]

    def put(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        json_data = json.loads(request.body)

        self.object.name = json_data["name"]
        self.object.price = json_data["price"]
        self.object.description = json_data["description"]
        self.object.is_published = json_data["is_published"]
        self.object.category_id = json_data["category_id"]

        self.object.save()

        return JsonResponse({
            "id": self.object.id,
            "name": self.object.name,
            "price": self.object.price,
            "description": self.object.description,
            "is_published": self.object.is_published,
            "category_id": self.object.category_id,
            "user_id": self.object.user_id,
            "image": self.object.image.url if self.object.image else None,
        })


@method_decorator(csrf_exempt, name='dispatch')
class AdDeleteView(DeleteView):
    model = Ad
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"status": "ok"}, status=204)


@method_decorator(csrf_exempt, name='dispatch')
class AdImageView(UpdateView):
    model = Ad
    fields = ["image"]

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.image = request.FILES["image"]

        self.object.save()

        return JsonResponse({
            "id": self.object.id,
            "name": self.object.name,
            "price": self.object.price,
            "description": self.object.description,
            "is_published": self.object.is_published,
            "category_id": self.object.category_id,
            "user_id": self.object.user_id,
            "image": self.object.image.url,
        })
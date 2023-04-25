import json

from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from users.models import Location, User


class LocationListView(ListView):
    model = Location

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        response = []
        for location in self.object_list:
            response.append({
                "id": location.id,
                "name": location.name,
                "lat": location.lat,
                "lng": location.lng,
            })

        return JsonResponse(response, safe=False)


class LocationDetailView(DetailView):
    model = Location

    def get(self, request, *args, **kwargs):
        location = self.get_object()

        return JsonResponse({
            "id": location.id,
            "name": location.name,
            "lat": location.lat,
            "lng": location.lng,
        })


@method_decorator(csrf_exempt, name='dispatch')
class LocationCreateView(CreateView):
    model = Location
    fields = ["name", "lat", "lng"]

    def post(self, request, *args, **kwargs):
        json_data = json.loads(request.body)

        location = Location.objects.create(
            name=json_data["name"],
            lat=json_data["lat"],
            lng=json_data["lng"],
        )

        return JsonResponse({
            "id": location.id,
            "name": location.name,
            "lat": location.lat,
            "lng": location.lng,
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class LocationUpdateView(UpdateView):
    model = Location
    fields = ["name", "lat", "lng"]

    def put(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        json_data = json.loads(request.body)

        self.object.name = json_data["name"]
        self.object.lat = json_data["lat"]
        self.object.lng = json_data["lng"]
        self.object.save()

        return JsonResponse({
            "id": self.object.id,
            "name": self.object.name,
            "lat": self.object.lat,
            "lng": self.object.lng,
        })


@method_decorator(csrf_exempt, name='dispatch')
class LocationDeleteView(DeleteView):
    model = Location
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"status": "ok"}, status=204)


@method_decorator(csrf_exempt, name='dispatch')
class UserListView(ListView):
    model = User

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        response = []
        for user in self.object_list.annotate(ads=Count('ad', filter=Q(ad__is_published=True))):
            response.append({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "role": user.role,
                "age": user.age,
                "locations": [loc.name for loc in user.locations.all()],
                "total_ads": user.ads,
            })

        return JsonResponse(response, safe=False)


class UserDetailView(DetailView):
    model = User

    def get(self, request, *args, **kwargs):
        user = self.get_object()

        return JsonResponse({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "role": user.role,
            "age": user.age,
            "locations": [loc.name for loc in user.locations.all()],
        })


@method_decorator(csrf_exempt, name='dispatch')
class UserCreateView(CreateView):
    model = User
    fields = ["first_name", "last_name", "username", "password", "age"]

    def post(self, request, *args, **kwargs):
        json_data = json.loads(request.body)

        user = User.objects.create(
            first_name=json_data["first_name"],
            last_name=json_data["last_name"],
            username=json_data["username"],
            password=json_data["password"],
            age=json_data["age"],
        )

        for location in json_data["locations"]:
            location_obj, _ = Location.objects.get_or_create(name=location) # Назначаем локацию,
            # либо создаем новую, если ее нет
            user.locations.add(location_obj)

        return JsonResponse({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "role": user.role,
            "age": user.age,
            "locations": [loc.name for loc in user.locations.all()],
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ["first_name", "last_name", "username", "password", "role", "age", "locations"]

    def put(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        json_data = json.loads(request.body)

        self.object.first_name = json_data["first_name"]
        self.object.last_name = json_data["last_name"]
        self.object.username = json_data["username"]
        self.object.password = json_data["password"]
        self.object.role = json_data["role"]
        self.object.age = json_data["age"]

        for location in json_data["locations"]:
            try:
                location_obj = Location.objects.get(id=location)
            except Location.DoesNotExist:
                return JsonResponse({"error": "Location not found"}, status=404)
            self.object.locations.add(location_obj)

        self.object.save()

        return JsonResponse({
            "id": self.object.id,
            "first_name": self.object.first_name,
            "last_name": self.object.last_name,
            "username": self.object.username,
            "role": self.object.role,
            "age": self.object.age,
            "locations": [loc.name for loc in self.object.locations.all()],
        })


@method_decorator(csrf_exempt, name='dispatch')
class UserDeleteView(DeleteView):
    model = User
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"status": "ok"}, status=204)

from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import Cat, Toy, Photo
from .forms import FeedingForm
import uuid
import boto3

from .forms import FeedingForm

# Add these "constants" below the imports
S3_BASE_URL = 'https://s3-us-west-1.amazonaws.com/'
BUCKET = 'cat-collector-s4383'

class CatCreate(CreateView):
  model = Cat
  fields = ['name', 'breed', 'description', 'age']

class CatUpdate(UpdateView):
  model = Cat
  fields = ['breed', 'description', 'age']

class CatDelete(DeleteView):
  model = Cat
  success_url = '/cats/'

def home(request):
  return render(request, 'home.html')

def about(request):
  return render(request, 'about.html')

def cats_index(request):
  cats = Cat.objects.all()
  return render(request, 'cats/index.html', { 'cats': cats })

def cats_detail(request, cat_id):
  cat = Cat.objects.get(id=cat_id)
  toys_cat_doesnt_have = Toy.objects.exclude(id__in=cat.toys.all().values_list('id'))
  print(toys_cat_doesnt_have)
  # instantiate FeedingForm to be rendered in the template
  feeding_form = FeedingForm()
  return render(request, 'cats/detail.html', {
    # pass the cat and feeding_form as context
    'cat': cat, 'feeding_form': feeding_form, 'toys': toys_cat_doesnt_have
  })

def add_feeding(request, cat_id):
	# create the ModelForm using the data in request.POST
  form = FeedingForm(request.POST)
  # validate the form
  if form.is_valid():
    # don't save the form to the db until it
    # has the cat_id assigned
    new_feeding = form.save(commit=False)
    new_feeding.cat_id = cat_id
    new_feeding.save()
  return redirect('detail', cat_id=cat_id)

def add_photo(request, cat_id):
  # photo-file was added to request.FILES
  photo_file = request.FILES.get('photo-file', None)
  print('this is photo file', photo_file)
  # if photo-file is not empty
  # do the following
  if photo_file:
    # get boto3 client for S3 and set up the bucket name and file name for the photo file to be uploaded to S3
    s3 = boto3.client('s3')
    print('this is s3', s3)
    #  create a unique "key" for the object in S3
    key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
    print('this is key', key)
    # try to upload the file to S3 
    try:
      # first, upload the file to S3  and get the url of the file
      s3.upload_fileobj(photo_file, BUCKET, key)
      # print('this is s3', s3.upload_fileobj(photo_file, BUCKET, key))
      # url of the file in S3 (for the photo) is the base url + the key
      url = f"{S3_BASE_URL}{BUCKET}/{key}"
      print('this is url', url)
      #  create a new photo object and save it to the db
      photo = Photo(url=url, cat_id=cat_id)
      print('this is photo', photo)
      #  save the photo to the db and redirect to the detail view
      photo.save()
    except:
      #  if there is an error, print it to the console 
      print('An error occurred uploading file to S3')
  # redirect to the detail view for the cat
  return redirect('detail', cat_id=cat_id)
    
    

def assoc_toy(request, cat_id, toy_id):
  Cat.objects.get(id=cat_id).toys.add(toy_id)
  return redirect('detail', cat_id=cat_id)

class ToyList(ListView):
  model = Toy

class ToyDetail(DetailView):
  model = Toy

class ToyCreate(CreateView):
  model = Toy
  fields = '__all__'

class ToyUpdate(UpdateView):
  model = Toy
  fields = ['name', 'color']

class ToyDelete(DeleteView):
  model = Toy
  success_url = '/toys/'
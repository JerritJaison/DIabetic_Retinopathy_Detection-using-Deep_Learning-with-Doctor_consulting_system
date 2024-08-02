# importing required packages

from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from diab_retina_app import process
from .models import *
from django.contrib.auth import authenticate, login

from keras.models import load_model  # TensorFlow is required for Keras to work
from PIL import Image, ImageOps  # Install pillow instead of PIL
import numpy as np
import matplotlib.pyplot as plt
import os
from django.http import JsonResponse


@csrf_exempt
def display(request):
    if request.method == "GET":
        return render(request, "predict.html")


@csrf_exempt
def process_image(request):
    if request.method == "POST":
        imagefile = request.FILES["image"]
        print("IMAGE", imagefile)
        upload_folder = r"static/media/"
        image_path = os.path.join(upload_folder, imagefile.name)
        print("Saving started...")
        with open(image_path, "wb+") as destination:
            for chunk in imagefile.chunks():
                destination.write(chunk)

        # Now 'image_path' contains the path to the uploaded image
        print("Image saved at:", image_path)
        # response = process.process_img(img)

        # Disable scientific notation for clarity
        np.set_printoptions(suppress=True)

        # Load the model
        model = load_model("my_model.h5", compile=False)

        # Load the labels
        class_names = open("labels.txt", "r").readlines()

        # Create the array of the right shape to feed into the keras model
        # The 'length' or number of images you can put into the array is
        # determined by the first position in the shape tuple, in this case 1
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

        # Replace this with the path to your image
        image = Image.open(image_path).convert("RGB")

        # resizing the image to be at least 224x224 and then cropping from the center
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

        # turn the image into a numpy array
        image_array = np.asarray(image)

        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

        # Load the image into the array
        data[0] = normalized_image_array

        # Predicts the model
        prediction = model.predict(data)
        index = np.argmax(prediction)
        class_name = class_names[index]
        confidence_score = prediction[0][index]

        # Print prediction and confidence score
        print("Class:", class_name[2:], end="")
        print("Confidence Score:", confidence_score)
        html_content = f"<span>{class_name[2:]}</span>"
        # run the inference
        prediction = model.predict(data)
        # print(prediction)

        # determining predicted result
        pred_new = prediction[0]
        pred = max(pred_new)

        print(pred_new)
        index = pred_new.tolist().index(pred)

        # heights of bars
        height = pred_new.tolist()
        new_height = [round(h * 100, 2) for h in height]

        # x-coordinates of left sides of bars
        left = range(1, len(new_height) + 1)

        tick_label = ["No DR", "Mild", "Moderate", "Severe", "Proliferative"]

        # plotting a bar chart
        plt.bar(
            left, new_height, tick_label=tick_label, width=0.8, color=["red", "green"]
        )

        # naming the x-axis
        plt.xlabel("Classes")
        # naming the y-axis
        plt.ylabel("Confidence (%)")
        # plot title
        plt.title("Diabetic Retinopathy Prediction")

        # function to show the plot
        # output_path = os.path.join(BASE_DIR, "static/output/graph.png")
        # plt.savefig(output_path)
        plt.show()

        return HttpResponse(html_content, status=200)


def index(request):
    return render(request, "index.html")


def signin(request):
    # abc=Login.objects.create_user(username='admin@gmail.com',password='admin',userType='Admin',viewPass='admin')
    # abc=Login.objects.filter(username='admin@gmail.com').update(viewPass='admin')
    if request.POST:
        email = request.POST["email"]
        password = request.POST["password"]
        if Login.objects.filter(username=email, viewPass=password).exists():
            data = authenticate(username=email, password=password)
            if data is not None:
                login(request, data)
                if data.userType == "User":
                    id = data.id
                    request.session["uid"] = id
                    resp = '<script>alert("Login Success"); window.location.href = "/userHome";</script>'
                    return HttpResponse(resp)
                elif data.userType == "Doctor":
                    id = data.id
                    request.session["uid"] = id
                    resp = '<script>alert("Login Success"); window.location.href = "/doctorHome";</script>'
                    return HttpResponse(resp)
                elif data.userType == "Admin":
                    resp = '<script>alert("Login Success"); window.location.href = "/adminHome";</script>'
                    return HttpResponse(resp)
            else:
                return HttpResponse(
                    "<script>alert('You are not Approved');window.location.href='/login'</script>"
                )
        else:
            return HttpResponse(
                "<script>alert('Invalid Username/Password');window.location.href='/login'</script>"
            )
    return render(request, "login.html")


def register(request):
    if request.POST:
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        address = request.POST["address"]
        password = request.POST["password"]
        image = request.FILES["imgfile"]
        if not Login.objects.filter(username=email).exists():
            logQry = Login.objects.create_user(
                username=email,
                password=password,
                userType="User",
                viewPass=password,
            )
            logQry.save()
            if logQry:
                regQry = Patient.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    address=address,
                    loginid=logQry,
                    image=image,
                )
                regQry.save()
                if regQry:
                    return HttpResponse(
                        "<script>alert('Registration Successful');window.location.href='/login';</script>"
                    )
        else:
            return HttpResponse(
                "<script>alert('Email Already Exists');window.location.href='/register';</script>"
            )
    return render(request, "register.html")


def doctorReg(request):
    if request.POST:
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        specialization = request.POST["specialization"]
        gender = request.POST["gender"]
        address = request.POST["address"]
        password = request.POST["password"]
        image = request.FILES["imgfile"]

        if not Login.objects.filter(username=email).exists():
            logQry = Login.objects.create_user(
                username=email,
                password=password,
                userType="Doctor",
                viewPass=password,
                is_active=0,
            )
            logQry.save()
            if logQry:
                regQry = Doctor.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    specialization=specialization,
                    gender=gender,
                    address=address,
                    image=image,
                    loginid=logQry,
                )
                regQry.save()
                if regQry:
                    return HttpResponse(
                        "<script>alert('Registration Successful');window.location.href='/login';</script>"
                    )
        else:
            return HttpResponse(
                "<script>alert('Email Already Exists');window.location.href='/doctorReg';</script>"
            )
    return render(request, "doctorReg.html")


############################################-USER-####################################################
def userHome(request):
    return render(request, "USER/userHome.html")


from datetime import datetime


def userViewDoctors(request):
    data = Doctor.objects.all()
    print(data)
    current_date = datetime.now().date()
    print(current_date)
    uid = request.session["uid"]
    UID = Patient.objects.get(loginid__id=uid)
    if request.POST:
        date = request.POST["date"]
        time = request.POST["time"]
        did = request.POST["did"]
        DID = Doctor.objects.get(id=did)
        bookNow = Appointments.objects.create(
            user=UID, doctor=DID, date=date, time=time
        )
        return HttpResponse(
            "<script>alert('Successfully Booked');window.location.href='/userViewDoctors';</script>"
        )
    return render(
        request, "USER/viewDoctors.html", {"data": data, "date": current_date}
    )


def myBookings(request):
    uid = request.session["uid"]
    data = Appointments.objects.filter(user__loginid=uid)
    return render(request, "USER/viewBookings.html", {"data": data})


############################################-ADMIN-####################################################


def adminHome(request):
    return render(request, "ADMIN/adminHome.html")


def viewDoctors(request):
    data = Doctor.objects.all()
    print(data)
    return render(request, "ADMIN/viewDoctors.html", {"data": data})


def viewPatients(request):
    data = Patient.objects.all()
    print(data)
    return render(request, "ADMIN/viewPatients.html", {"data": data})


def manageUsers(request):
    id = request.GET["id"]
    status = request.GET["status"]
    if status == "1":
        approve = Login.objects.filter(id=id).update(is_active=1)
    else:
        delete = Login.objects.filter(id=id).delete()
    return redirect("/viewDoctors")


############################################-DOCTOR-####################################################


def doctorHome(request):
    return render(request, "DOCTOR/doctorHome.html")

def viewBookings(request):
    uid = request.session["uid"]
    data = Appointments.objects.filter(doctor__loginid=uid)
    return render(request, "DOCTOR/viewBookings.html", {"data": data})


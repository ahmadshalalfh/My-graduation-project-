from django.shortcuts import render, redirect
from django.contrib import messages as django_messages
from .models import   users,Employee, WaterDepartmentRequests,  Announcements,News,myuser,Departments,Messages,Requests,Bills,Payments,Subscriptions,AdministrationDermentRequests ,ElectricityDepartmentRequests,WaterDepartmentRequests,Notices,EngineeringDepartmentRequests,ComplaintsDepartmentRequests
import bcrypt
from .decorators import admin_required ,employee_required ,citizen_required ,employee_and_admin
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password ,make_password
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
import base64
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def homepage(request):
    news = News.objects.all().order_by('-NewsID').first()
    announcements = Announcements.objects.all().order_by('-AnnouncementsID').first()
    
    if news:
        news.Newsimage = base64.b64encode(news.Newsimage).decode('utf-8')
    
    if announcements:
        announcements.Announcementsimage = base64.b64encode(announcements.Announcementsimage).decode('utf-8')
    
    context = {
        'news': news,
        'announcements': announcements,
    }
    employee = None
    if request.user.is_authenticated:
        try:
         employee = Employee.objects.get(userID=request.user.userID)
    
         context['employee'] = employee
        except Employee.DoesNotExist:
            pass
    return render(request,'pages/homepage.html' ,context)
 

def login(request):

    if request.method == 'POST':
       ID = request.POST.get('ID')
       password = request.POST.get('password')
        
       
       try:
          user = myuser.objects.get(userID=ID)
          
          if check_password(password, user.password):
            auth_login(request , user)
            return redirect (homepage)
          else:
             django_messages.error(request, ' كلمة المرور خاطئه')

       except myuser.DoesNotExist:
        
            django_messages.error(request, 'المستخدم ليس لدية حساب ')
            
    return render(request, 'pages/login.html')

def registration(request):
    if request.method == 'POST' :
       ID = request.POST.get('ID')
       email = request.POST.get('email')
       rpassword = request.POST.get("rpassword")
       password = request.POST.get('password')
       phone = request.POST.get('phon')
       address = request.POST.get('address')
       
       try:
            citizen = users.objects.get(ID=ID) 
            try:
                user = myuser.objects.get(userID = ID)   
                django_messages.error(request, 'رقم المستخدم {} لديه حساب '.format(ID))
            except myuser.DoesNotExist:
                if password == rpassword:
                    user = myuser.objects.create_user(userID = ID , username = citizen.username ,password = password , Phone = phone ,Address = address , email =email  )
                    return redirect('login')
                else:
                    django_messages.error(request, 'كلمة المرور غير متطابقة')
       except users.DoesNotExist:
            django_messages.error(request, 'رقم المستخدم {} غير موجود  '.format(ID))
        
    return render(request, 'pages/registration.html')

def logout_view(request):
    logout(request)
    return redirect('homepage')
    

@admin_required
def registration_emploee(request):
    Department = Departments.objects.all()
   
    if request.method == 'POST':
        ID = request.POST.get('ID')
        name = request.POST.get('name')
        email = request.POST.get('email')
        rpassword = request.POST.get("rpassword")
        password = request.POST.get('password')
        phone = request.POST.get('phon')
        address = request.POST.get('address')
        department_id = int(request.POST.get('department'))
        department = get_object_or_404(Departments, DepartmentID=department_id)


        try :
              employee = Employee.objects.get(userID = ID)
              django_messages.error(request, 'رقم المستخدم {} موجود  '.format(ID))
        except:
            if password == rpassword:
                    user = Employee.objects.create_user(is_employee = 1 , department = department, userID = ID , username = name ,password = password , Phone = phone ,Address = address , email =email )

                    
                    return render(request, 'pages/admin/employee_accounts.html')
            else:
                    django_messages.error(request, 'كلمة المرور غير متطابقة')
         
        

    return render(request, 'pages/registration_emploee.html', {'Department': Department})

   
@employee_required
def requests_table(request):
    userid = request.user.userID
    employee = get_object_or_404(Employee, userID=userid)
    depid = employee.department

    requestspaid = Requests.objects.filter(DepartmentID = depid, Status = 'PA')
    
    
    if employee.department.DepartmentID != 4 :  
     requestsdata = Requests.objects.filter(DepartmentID = depid , Status = None , ID_Photo__isnull=False )
    else:
     req = Requests.objects.filter( Status = 'AC' )
     unpaid_requests = []
     for request_item in req:
            havebill = Bills.objects.filter(RequestID=request_item).exists()
            if not havebill:
                unpaid_requests.append(request_item)
                requestsdata = unpaid_requests


    return render (request , 'pages/requests.html', {'requestsdata': requestsdata, 'employee': employee , 'requestspaid':requestspaid} )
@employee_required
def view_request(request, requestid):
    userid = request.user.userID
    employee = get_object_or_404(Employee, userID=userid)
    depid = employee.department
    
    if depid == get_object_or_404(Departments, DepartmentID=1) :
     requestobj = ElectricityDepartmentRequests.objects.filter(RequestID =requestid )
     for req in requestobj:
       if req.BuildingPermit_Photo :
        req.BuildingPermit_Photo = base64.b64encode(req.BuildingPermit_Photo).decode('utf-8')
       if req.Oldsubscription_Photo :
        req.Oldsubscription_Photo = base64.b64encode(req.Oldsubscription_Photo).decode('utf-8')
       req.ID_Photo = base64.b64encode(req.ID_Photo).decode('utf-8')

    elif depid == get_object_or_404(Departments, DepartmentID=2) : 
     requestobj = WaterDepartmentRequests.objects.filter(RequestID =requestid )
     for req in requestobj:
       if req.BuildingPermit_Photo :
        req.BuildingPermit_Photo = base64.b64encode(req.BuildingPermit_Photo).decode('utf-8')
       if req.Oldsubscription_Photo :
        req.Oldsubscription_Photo = base64.b64encode(req.Oldsubscription_Photo).decode('utf-8')
       req.ID_Photo = base64.b64encode(req.ID_Photo).decode('utf-8')

    elif depid == get_object_or_404(Departments, DepartmentID=3) :
     requestobj = AdministrationDermentRequests.objects.filter(RequestID =requestid )
     for req in requestobj:
       req.Bill_Photo = base64.b64encode(req.Bill_Photo).decode('utf-8')
       if req.Rent_Photo :
        req.Rent_Photo = base64.b64encode(req.Rent_Photo).decode('utf-8')
       req.ID_Photo = base64.b64encode(req.ID_Photo).decode('utf-8')

    elif depid == get_object_or_404(Departments, DepartmentID=5) :
     requestobj = EngineeringDepartmentRequests.objects.filter(RequestID =requestid )
     for req in requestobj:
       req.Ownership_Photo = base64.b64encode(req.Ownership_Photo).decode('utf-8')
       if req.SpacePlan_Photo :
        req.SpacePlan_Photo = base64.b64encode(req.SpacePlan_Photo).decode('utf-8')
       if req.CertifiedEngineeringPlan_Photo :
        req.CertifiedEngineeringPlan_Photo = base64.b64encode(req.CertifiedEngineeringPlan_Photo).decode('utf-8')
       if req.Geometricscheme_Photo : 
        req.Geometricscheme_Photo = base64.b64encode(req.Geometricscheme_Photo).decode('utf-8')
       if req.CourtAffidavit_Photo :  
        req.CourtAffidavit_Photo = base64.b64encode(req.CourtAffidavit_Photo).decode('utf-8')
       req.ID_Photo = base64.b64encode(req.ID_Photo).decode('utf-8')
    return render(request, 'pages/view_request.html', {'requestobj': requestobj , 'employee':employee} )

@admin_required
def accounts_management (request):

    return render (request , 'pages/admin/accounts_management.html')

@admin_required
def citizens_accounts (request):

   return render (request , 'pages/admin/citizens_accounts.html')
@admin_required
def employee_accounts (request):

   return render (request , 'pages/admin/employee_accounts.html')


@employee_and_admin
def Updating_deleting_citizen (request):
   users = myuser.objects.filter(is_employee = 0 , is_admin = 0 )
   return render (request , 'pages/admin/Updating_deleting_citizen.html' ,{ 'users' : users })

@admin_required
def Updating_deleting_employee (request):
   users = Employee.objects.filter(is_employee=1)

   return render(request, 'pages/admin/Updating_deleting_employee.html', {'users': users})

 
def updating_citizen(request , userid ):
    user1 = myuser.objects.filter(userID = userid).first()
    if request.method == 'POST':
        new_username = request.POST.get('name')
        new_email = request.POST.get('email')
        new_password = request.POST.get('password')
        new_address = request.POST.get('address')
        new_phone = request.POST.get('phone')
        
        user_instance  = myuser.objects.get(userID=userid)

        user_instance .username = new_username
        user_instance .email = new_email
        user_instance .password = make_password(new_password)
        user_instance .address = new_address
        user_instance .phone = new_phone
        
       
        user_instance.save()
        return redirect('Updatingdeletingcitizen')

        
    

    return render ( request , 'pages/admin/updating_citizen.html', {'user1': user1})

@admin_required
def updating_employee(request , userid ):
    user1 = Employee.objects.filter(userID = userid).first()
    Department = Departments.objects.all()
    if request.method == 'POST':
        new_username = request.POST.get('name')
        new_email = request.POST.get('email')
        new_password = request.POST.get('password')
        new_address = request.POST.get('address')
        new_phone = request.POST.get('phone')
        new_department = request.POST.get('department')
        new_department = get_object_or_404(Departments, DepartmentID=new_department)
        
        user_instance  = Employee.objects.get(userID=userid)

        user_instance .username = new_username
        user_instance .email = new_email
        user_instance .password = make_password(new_password)
        user_instance .address = new_address
        user_instance .phone = new_phone
        user_instance .department = new_department
        
       
        user_instance.save()
        return redirect('Updating_deleting_employee')

        
    

    return render ( request , 'pages/admin/updating_employee.html', {'user1': user1 , 'Department': Department} )
@admin_required
def delete_employee(request , userid):

    user =  Employee.objects.get(userID = userid)
    user.delete()
    return redirect ('Updating_deleting_employee') 
@admin_required
def news_announcements(request):

    return render(request , 'pages/admin/news_announcements.html')
@admin_required
def announcements(request):

    if request.method == 'POST':
        newstitle = request.POST.get('newstitle')
        newscontent = request.POST.get('newscontent')
        newsimage = request.FILES.get('image')
        date = timezone.localtime(timezone.now())
        
        if newsimage :
         newsimage_content = newsimage.read()
         newsimage = newsimage_content
         Announcements.objects.create(
            Title = newstitle ,
            Content = newscontent, 
            Date = date ,
            Announcementsimage = newsimage  )
         return redirect ('news_announcements') 
    return render(request , 'pages/admin/announcements.html')
@admin_required
def news(request):
    if request.method == 'POST':
        newstitle = request.POST.get('newstitle')
        newscontent = request.POST.get('newscontent')
        newsimage = request.FILES.get('newsimage')
        date = timezone.localtime(timezone.now())
        
        if newsimage :
         newsimage_content = newsimage.read()
         newsimage = newsimage_content
        News.objects.create(Title = newstitle ,Content = newscontent, Date = date , Newsimage = newsimage  )
        return redirect ('news_announcements') 

    return render(request , 'pages/admin/news.html')

def services (request):
    

    return render(request , 'pages/citizen/services.html')

def service_details (request , num , num1):
    if num == 1 :
     return render(request , 'pages/citizen/service_details1.html', {'num1': num1}  )
    elif num == 2 :
      return render(request , 'pages/citizen/service_details2.html', {'num1': num1}  )
    elif num == 3 :
      return render(request , 'pages/citizen/service_details3.html')
    elif num == 5 :
     return render(request , 'pages/citizen/service_details5.html', {'num1': num1}  )
    elif num == 4 :
     return render(request , 'pages/citizen/service_details4.html', {'num1': num1}  )

    

@citizen_required
def Addressverification(request):
    if request.method == 'POST':
        details = request.POST.get('details')
        id_image = request.FILES.get('id_image')
        bill_image = request.FILES.get('bill_image')
        rent_image  = request.FILES.get('rent')
        date = timezone.localtime(timezone.now())
        userid = request.user.userID
        userid = get_object_or_404(myuser, userID=userid)
        dep = get_object_or_404(Departments, DepartmentID=3)
        if id_image:
            id_image_content = id_image.read()
            id_image = id_image_content
        if bill_image:
            building_image_content = bill_image.read()
            bill_image = building_image_content
        if rent_image :
            building_image_content = rent_image .read()
            rent_image  = building_image_content
        
        
        AdministrationDermentRequests.objects.create(
            RequestDate=date, 
            Details=details, 
            ID_Photo=id_image, 
            CitizenID=userid, 
            DepartmentID=dep, 
            Bill_Photo=bill_image,
            Rent_Photo = rent_image,
            Type = 'طلب شهادة إثبات سكن'

        )
        django_messages.error(request, 'تم تقديم طلبك بنجاح ')
    
        return redirect('services')
    return render(request, 'pages/citizen/Addressverification.html')
@citizen_required
def  electricity_subscription(request,num1):
    if request.method == 'POST':
        details = request.POST.get('details')
        id_image = request.FILES.get('id_image')
        build_image = request.FILES.get('build_image')
        oldsup_image = request.FILES.get('oldsup_image')
        date = timezone.localtime(timezone.now())
        userid = request.user.userID
        userid = get_object_or_404(myuser, userID=userid)
        dep = get_object_or_404(Departments, DepartmentID=1)
        if id_image:
            id_image_content = id_image.read()
            id_image = id_image_content
        if build_image:
            building_image_content = build_image.read()
            build_image = building_image_content

        if oldsup_image:
            oldsub_image_content = oldsup_image.read()
            oldsup_image = oldsub_image_content
        
        if num1 == 1:
         ElectricityDepartmentRequests.objects.create(
            RequestDate=date, 
            Details=details, 
            ID_Photo=id_image, 
            CitizenID=userid, 
            DepartmentID=dep, 
            BuildingPermit_Photo=build_image,
            Type = 'تمديد اشتراك كهرباء جديد'

         )
        elif num1 == 2 :
            ElectricityDepartmentRequests.objects.create(
            RequestDate=date, 
            Details=details, 
            ID_Photo=id_image, 
            CitizenID=userid, 
            DepartmentID=dep, 
            Oldsubscription_Photo=oldsup_image,
            Type = ' فصل اشتراك عداد كهرباء ')
        elif num1 == 3 :
            ElectricityDepartmentRequests.objects.create(
            RequestDate=date, 
            Details=details, 
            ID_Photo=id_image, 
            CitizenID=userid, 
            DepartmentID=dep, 
            Oldsubscription_Photo=oldsup_image,
            Type = 'وصل اشتراك عداد كهرباء')
        django_messages.error(request, 'تم تقديم طلبك بنجاح ')

        return redirect('services')
    
    return render(request, 'pages/citizen/electricity_subscription.html', {'num1':num1})
@citizen_required
def  Water_subscription(request , num1):
    if request.method == 'POST':
        details = request.POST.get('details')
        id_image = request.FILES.get('id_image')
        build_image = request.FILES.get('build_image')
        oldsup_image = request.FILES.get('oldsup_image') 
        date = timezone.localtime(timezone.now())
        userid = request.user.userID
        userid = get_object_or_404(myuser, userID=userid)
        dep = get_object_or_404(Departments, DepartmentID=2)
        if id_image:
            id_image_content = id_image.read()
            id_image = id_image_content
        if build_image:
            building_image_content = build_image.read()
            build_image = building_image_content
        if oldsup_image:
            oldsub_image_content = oldsup_image.read()
            oldsup_image = oldsub_image_content
       
        
        if num1 == 1 :
         WaterDepartmentRequests.objects.create(
            RequestDate=date, 
            Details=details, 
            ID_Photo=id_image, 
            CitizenID=userid, 
            DepartmentID=dep, 
            BuildingPermit_Photo=build_image,
            Type = 'تمديد اشتراك مياه جديد'

         )
        elif num1 == 2 :
            WaterDepartmentRequests.objects.create(
            RequestDate=date, 
            Details=details, 
            ID_Photo=id_image, 
            CitizenID=userid, 
            DepartmentID=dep, 
            Oldsubscription_Photo=oldsup_image,
            Type = ' فصل إشتراك عداد مياه'

         )
        elif num1 == 3:
            WaterDepartmentRequests.objects.create(
            RequestDate=date, 
            Details=details, 
            ID_Photo=id_image, 
            CitizenID=userid, 
            DepartmentID=dep, 
            Oldsubscription_Photo=oldsup_image,
            Type = ' وصل إشتراك عداد مياه'

         )
        django_messages.error(request, 'تم تقديم طلبك بنجاح ')

        return redirect('services')
    
    return render(request, 'pages/citizen/Water_subscription.html' , {'num1':num1})
@employee_required
def delete_request (request , requestid):
    req = Requests.objects.get(RequestID = requestid)
    req.delete()
    citizenid = req.CitizenID.userID
    citizenid = get_object_or_404(myuser, userID=citizenid)
    date = timezone.localtime(timezone.now())
    Notices.objects.create(CitizenID =citizenid , Details = 'تم رفض الطلب رقم {}' .format(requestid) , DueDate = date )

    return redirect( 'requests_table')
@employee_required
def accept_request (request , requestid):
    req = Requests.objects.get(RequestID = requestid)
    req.Status = "AC"
    req.save()
    citizenid = req.CitizenID.userID
    citizenid = get_object_or_404(myuser, userID=citizenid)
    date = timezone.localtime(timezone.now())
    Notices.objects.create(CitizenID =citizenid , Details = 'تم قبول الطلب رقم  {} بنجاح' .format(requestid) , DueDate = date )
    

    return redirect( 'requests_table')


def Notice (request):
    notices = None
    if request.user.is_authenticated:
     notices = Notices.objects.filter(CitizenID = request.user.userID ).order_by('-DueDate')
    


    return render(request , 'pages/citizen/Notice.html' , {'notices':notices})




@employee_required
def creat_bills (request ,requestid):
    userid = request.user.userID
    employee = get_object_or_404(Employee, userID=userid)
    req = Requests.objects.filter(RequestID = requestid).first()
    if request.method == 'POST':
       reqid = get_object_or_404(Requests, RequestID=requestid)
       citizenid = req.CitizenID.userID
       citizenid = get_object_or_404(myuser, userID=citizenid)
       amount = request.POST.get('amount')
       date = timezone.localtime(timezone.now())

       Bills.objects.create(
          
         RequestID = reqid ,
         CitizenID = citizenid,
         Amount = amount,
         DueDate = date,
         paid = 0
       )

       Notices.objects.create(
           CitizenID = citizenid,
           Details = 'تم اصدار فاتوره للطلب الخاص بك ذو الرقم {} ' .format(requestid),
           DueDate = date
       )
       return redirect ('requests_table' )


    return render(request , 'pages/creat_bills.html' , {'req':req ,'employee':employee } )
@citizen_required
def bills(request):
    citizenid = get_object_or_404(myuser, userID=request.user.userID)
    bills = Bills.objects.filter(CitizenID=citizenid).order_by('-DueDate')
    bill_images = []  # قائمة لتخزين الصور
    context = {}
       
    
    # إنشاء صورة لكل فاتورة
    for bill in bills:
       img_str = create_invoice(bill)
       bill_images.append( img_str)
       context = {
        'data': zip(bills, bill_images)
    }

    return render(request, 'pages/citizen/bills.html' , context )




def create_invoice(bill):
    # Create a new image with larger dimensions to improve the design
    img_width, img_height = 800, 800
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Define fonts and colors
    title_font = ImageFont.truetype("arialbd.ttf", size=36)
    regular_font = ImageFont.truetype("arial.ttf", size=28)
    label_font = ImageFont.truetype("arial.ttf", size=24)
    text_color = (45,46,50) # Black color
    header_color = (60,154,241)  # Blue color for header
    border_color = (45,46,50)  # Black border color
    
    
    # Draw a border around the invoice
    margin = 10
    draw.rectangle([(margin, margin), (img_width-margin, img_height-margin)], outline=border_color, width=2)
    
    # Add the invoice title with a decorative background
    draw.rectangle([(margin, 60), (img_width - margin, 120)], fill=header_color)
    draw.text((margin + 20, 70), 'Tarqumia Municipality Invoice', fill='white', font=title_font)
    
    # Draw a light gray background for the labels with an orange bottom line
    y_offset = 160
    x_start = 50
    spacing = 200
    line_height = 60  # Increased line height for better readability
    y_end = img_height - margin  # End position for labels

    # Function to draw lines between rows
    def draw_lines(start, end, num_lines, draw_obj):
        line_spacing = (end - start) // num_lines
        for i in range(1, num_lines):
            y = start + i * line_spacing
            draw_obj.line([(x_start, y), (x_start + spacing * 2, y)], fill=text_color, width=1)

    # Draw lines between rows
    draw_lines(y_offset, y_end, 4, draw)

    # Add the labels
    draw.text((x_start, y_offset), 'Invoice Number', fill=text_color, font=label_font)
    draw.text((x_start, y_offset + line_height * 2), 'Amount', fill=text_color, font=label_font)
    draw.text((x_start, y_offset + line_height * 4), 'Customer ID', fill=text_color, font=label_font)
    draw.text((x_start, y_offset + line_height * 6.5), 'Due Date', fill=text_color, font=label_font)
    
    # Add the values below the labels
    draw.text((x_start + spacing, y_offset), f'{bill.BillID}', fill=text_color, font=regular_font)
    draw.text((x_start + spacing, y_offset + line_height * 2), f'₪{bill.Amount}', fill=text_color, font=regular_font)
    draw.text((x_start + spacing, y_offset + line_height * 4), f'{bill.CitizenID.userID}', fill=text_color, font=regular_font)
    draw.text((x_start + spacing, y_offset + line_height * 6.5), f'{bill.DueDate}', fill=text_color, font=regular_font)

    # Convert the image to Base64 data
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return img_str

@citizen_required
def  engineering_department_requests(request,num1):
    if request.method == 'POST':
        details = request.POST.get('details')
        id_image = request.FILES.get('id_image')
        Title_Deed_Image = request.FILES.get('Title_Deed_Image')
        Plot_Plan_Image = request.FILES.get('Plot_Plan_Image')
        Certified_Area_Image = request.FILES.get('Certified_Area_Image')
        Court_Affidavit_Image = request.FILES.get('Court_Affidavit_Image')
        Engineering_Plan_image = request.FILES.get('Engineering_Plan_image')
        date = timezone.localtime(timezone.now())
        userid = request.user.userID
        userid = get_object_or_404(myuser, userID=userid)
        dep = get_object_or_404(Departments, DepartmentID=5)
        if id_image:
            id_image_content = id_image.read()
            id_image = id_image_content
        

        if Plot_Plan_Image:
            oldsub_image_content = Plot_Plan_Image.read()
            Plot_Plan_Image = oldsub_image_content

        if Title_Deed_Image:
            oldsub_image_content = Title_Deed_Image.read()
            Title_Deed_Image = oldsub_image_content

        if Certified_Area_Image:
            oldsub_image_content = Certified_Area_Image.read()
            Certified_Area_Image = oldsub_image_content

        if Court_Affidavit_Image:
            oldsub_image_content = Court_Affidavit_Image.read()
            Court_Affidavit_Image = oldsub_image_content

        if Engineering_Plan_image:
            oldsub_image_content = Engineering_Plan_image.read()
            Engineering_Plan_image = oldsub_image_content
        
        
        if num1 == 1 :
            EngineeringDepartmentRequests.objects.create(
            RequestDate=date, 
            Details=details, 
            ID_Photo=id_image, 
            CitizenID=userid, 
            DepartmentID=dep, 
            Ownership_Photo=Title_Deed_Image,
            Type = 'طلب شهادة اثبات ملكية'
            )

        elif num1 == 2 :
            EngineeringDepartmentRequests.objects.create(
            RequestDate=date, 
            Details=details, 
            ID_Photo=id_image, 
            CitizenID=userid, 
            DepartmentID=dep, 
            Ownership_Photo=Title_Deed_Image,
            Geometricscheme_Photo = Plot_Plan_Image ,
            Type = 'ترسيم حدود لقطع الأراضي')

        elif num1 == 3:
         EngineeringDepartmentRequests.objects.create(
            RequestDate=date, 
            Details=details, 
            ID_Photo=id_image, 
            CitizenID=userid, 
            DepartmentID=dep, 
            SpacePlan_Photo =Certified_Area_Image ,
            Ownership_Photo = Title_Deed_Image ,
            CourtAffidavit_Photo = Court_Affidavit_Image,
            CertifiedEngineeringPlan_Photo = Engineering_Plan_image,
            Type = 'طلب رخصة بناء جديد'

         )
        django_messages.error(request, 'تم تقديم طلبك بنجاح ')

        return redirect('services')
    
    return render(request, 'pages/citizen/engineering_department_requests.html', {'num1':num1})

@employee_required
def payments (request):
    date = timezone.localtime(timezone.now())
    employee = Employee.objects.get(userID=request.user.userID)

    if request.method == 'POST':
     billid = request.POST.get('bill_id')
     try:
        
        
        Bills.objects.get(BillID = billid)
       
        bill_id = get_object_or_404(Bills, BillID=billid)
        bill = Bills.objects.get(BillID = billid ) 
        amount_paid = float(request.POST.get('amount_paid'))
        userid =bill.CitizenID.userID
        userid = get_object_or_404(myuser, userID=userid)
        reqid = bill.RequestID.RequestID
        payment = Payments.objects.filter(BillID = bill_id)
        requ = Requests.objects.get(RequestID = reqid)
        total = 0
     
        for paymen in payment :
                total = total + paymen.AmountPaid 
                
        remainingamount = (bill.Amount - total) - amount_paid
        
        if not bill.paid:
            
            
            if remainingamount == 0 :
                
                Payments.objects.create(
                    BillID = bill_id,
                    AmountPaid =  amount_paid,
                    PaymentDate = date
                    ) 
                Notices.objects.create(
                    CitizenID =userid ,
                    Details = 'تم تسديد قيمت الفاتوره  الرقم {} بالكامل  ' .format(bill.BillID) ,
                    DueDate = date
                )
               
                bill.paid = 1
                bill.save()
                requ.Status = 'PA'
                requ.save()
                
                return redirect('homepage')
                

            elif remainingamount > 0 :
                
                Payments.objects.create(
                    BillID = bill_id,
                    AmountPaid =  amount_paid,
                    PaymentDate = date
                    ) 
                Notices.objects.create(
                    CitizenID = userid,
                    Details = '  تم تسديد {}  من قيمه الفاتوره رقم {} , متبقي {}    ' .format(amount_paid ,bill.BillID,remainingamount) ,
                    DueDate = date
                    )
                
                bill.save()
                

                return redirect('homepage')
                

            elif remainingamount < 0 :
                remainingamount = (bill.Amount - total)
                
                django_messages.error(request, 'المبلغ اكبر من قيمة الفاتوره , قيمة الفاتوره {} ' .format(remainingamount))
        else:
                          django_messages.error(request, '  الفاتوره رقم {} مدفوعه  ' .format(bill.BillID))

     except Bills.DoesNotExist :
            django_messages.error(request, ' رقم الفاتوره غير موجود ')
          

       
    return render(request , 'pages/payments.html' ,{'date':date , 'employee':employee})


def Subscription(request ,requestid):
    requ = Requests.objects.get(RequestID=requestid)
    if request.method == 'POST':
        name = request.POST.get('name')
        userid = requ.CitizenID.userID
        userid = get_object_or_404(myuser, userID=userid)
        departmentid = requ.DepartmentID.DepartmentID
        departmentid = get_object_or_404(Departments, DepartmentID=departmentid)
        sup_photo = request.FILES.get('build_image')
        if sup_photo:
            id_image_content = sup_photo.read()
            sup_photo = id_image_content

        Subscriptions.objects.create(
            Name = name,
            CitizenID = userid,
            DepartmentID = departmentid,
            Subscription_photo = sup_photo
        )
        requ.Status = 'DONE'
        requ.save()
        

        return redirect('requests_table')

    
    return render(request , 'pages/subscripions.html' ,{'requ':requ})
@citizen_required
def documents (request):
    citizenid = get_object_or_404(myuser, userID=request.user.userID)
    subscriptionall = Subscriptions.objects.filter(CitizenID = citizenid ).exclude(Q(DepartmentID=1) | Q(DepartmentID=2))
    for subscription in subscriptionall:
     if subscription.Subscription_photo :
        subscription.Subscription_photo = base64.b64encode(subscription.Subscription_photo).decode('utf-8')


    return render(request , 'pages/citizen/documents.html' ,{'subscriptionall':subscriptionall})

def news_and_announcements(request):
   
    news = News.objects.order_by('-NewsID').all()
    announcements = Announcements.objects.order_by('-AnnouncementsID').all()
    if news:
        for new in news :
          if new.Newsimage:
           new.Newsimage = base64.b64encode(new.Newsimage).decode('utf-8')
    if announcements:
        for announcement in announcements :
          if announcement.Announcementsimage :
           announcement.Announcementsimage = base64.b64encode(announcement.Announcementsimage).decode('utf-8')
    employee = None
    if request.user.is_authenticated:
        try:
            employee = Employee.objects.get(userID=request.user.userID)
        except Employee.DoesNotExist:
            employee = None

    context = {
        'news': news,
        'announcements': announcements,
        'employee': employee
    }

    return render(request, 'pages/news_and_announcements.html', context)

@citizen_required
def complaints(request ,num1):
   if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        date = timezone.localtime(timezone.now())
        userid = request.user.userID
        userid = get_object_or_404(myuser, userID=userid)
        dep1 = get_object_or_404(Departments, DepartmentID=1)
        dep2 = get_object_or_404(Departments, DepartmentID=2)
        if image:
            id_image_content = image.read()
            image = id_image_content
       
        
        if num1 == 1 :
         ComplaintsDepartmentRequests.objects.create(
            RequestDate=date, 
            Details=content, 
            Supportive_Photo=image, 
            CitizenID=userid, 
            DepartmentID=dep1, 
            Type = 'شكوى لقسم الكهرباء'

         )
        elif num1 == 2 :
           ComplaintsDepartmentRequests.objects.create(
            RequestDate=date, 
            Details=content, 
            Supportive_Photo=image, 
            CitizenID=userid, 
            DepartmentID=dep2, 
            Type = 'شكوى لقسم المياه' )
        django_messages.error(request, 'تم تقديم الشكوى بنجاح ')
           
        return redirect('services')
   
   
   return render(request , 'pages/citizen/complaints.html')
@employee_required
def complaints_tabel(request ):
   
    userid = request.user.userID
    employee = get_object_or_404(Employee, userID=userid)
    depid = employee.department

    requests = ComplaintsDepartmentRequests.objects.filter(DepartmentID = depid , Status = None)
   
    return render(request , 'pages/complaints_tabel.html' ,{'requests': requests})

@employee_required
def view_complaints(request , requestid ):

    complaints = ComplaintsDepartmentRequests.objects.filter(RequestID = requestid)
    for complaint in complaints:
       if complaint.Supportive_Photo :
         complaint.Supportive_Photo = base64.b64encode(complaint.Supportive_Photo).decode('utf-8')
   
    return render(request , 'pages/view_request.html' ,{'complaints':complaints})


def complaints_Done(request , requestid):
    req = Requests.objects.get(RequestID = requestid)
    req.Status = 'Done'
    req.save()
    citizenid = req.CitizenID.userID
    citizenid = get_object_or_404(myuser, userID=citizenid)
    date = timezone.localtime(timezone.now())
    Notices.objects.create(CitizenID =citizenid , Details = 'تم قرائة الشكوى رقم {} الخاصه بك وسيتم معالجة الامر في اقرب وقت' .format(requestid) , DueDate = date )

   
   
    return redirect('complaints_tabel')

def payments_bill(request , billid):
   Billid = get_object_or_404(Bills, BillID=billid)
   payments = Payments.objects.filter(BillID = Billid)
   
   return render(request , 'pages/citizen/payments_bill.html' , {'payments':payments})



def creat_notice (request , requestid):
       date = timezone.localtime(timezone.now())
   
       reqid = get_object_or_404(Requests, RequestID=requestid)
       citizenid = reqid.CitizenID.userID
       citizenid = get_object_or_404(myuser, userID=citizenid)
       Notices.objects.create(
           CitizenID = citizenid,
           Details = 'سيتم تلبية طلبك ذو الرقم {} في اسرع وقت ممكن  ' .format(requestid),
           DueDate = date
       )
       req = Requests.objects.get(RequestID = requestid)
       req.Status = 'Done'
       req.save()
    


       return redirect( 'requests_table')


def messages(request):

   my_messages = Messages.objects.filter(receiver = request.user.userID )
   return render (request , 'pages/messages.html' , {'my_messages':my_messages}) 

def create_message(request):
    Department = Departments.objects.all()
    if request.method == 'POST':
        sender = request.user.userID
        receiver = request.POST.get('employeeSelect')
        date = timezone.localtime(timezone.now())
        content = request.POST.get('text')
        
        sender = get_object_or_404(myuser, userID=sender)
        receiver = get_object_or_404(myuser, userID=receiver)
        Messages.objects.create(sender=sender, receiver=receiver, Content=content, SendDate=date)
        return redirect('messages')
    return render(request ,'pages/create_message.html' ,{'Department': Department} )

def get_employees_by_department(request, department_id):
    
   departmentid = get_object_or_404(Departments, DepartmentID=department_id)
   employees = Employee.objects.filter(department=departmentid).values('userID', 'username')   
   employees_list = list(employees)    
   return JsonResponse(employees_list, safe=False)


def about(request):
   
   return render(request, 'pages/about.html')


def subscripions (request):
    citizenid = get_object_or_404(myuser, userID=request.user.userID)
    subscriptionall = Subscriptions.objects.filter(CitizenID = citizenid ).filter(Q(DepartmentID=1) | Q(DepartmentID=2))
    for subscription in subscriptionall:
     if subscription.Subscription_photo :
        subscription.Subscription_photo = base64.b64encode(subscription.Subscription_photo).decode('utf-8')


    return render(request , 'pages/citizen/subscripions.html' ,{'subscriptionall':subscriptionall})
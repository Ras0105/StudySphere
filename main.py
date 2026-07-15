# -------Imports-Basic-------------------------------------------------
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from bson import ObjectId
# -------Imports-Password-------------------------------------------------
from passlib.context import CryptContext

# -------Imports-Session-------------------------------------------------
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os

# -------Imports-Secret Code-------------------------------------------------
import secrets

# -------Imports-Image----------------------------------------------------
import uuid
import shutil

# -------Imports-OTP----------------------------------------------------
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

# -------Imports-Database-------------------------------------------------
from database import collections

# -------Load-Environment-Variables-------------------------------------------------
# -------from .env file------------------------------------------------------
load_dotenv()

# -------Temporary OTP Storage------------------------------------------------------
reset_otp={}


# -------Session/ Registration/ OTP-------------------------------------------------
SECRET_KEY=os.getenv("SECRET_KEY")
MONGODB_URI=os.getenv("MONGODB_URI")
DATABASE_NAME=os.getenv("DATABASE_NAME")
EMAIL_ADDRESS=os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD=os.getenv("EMAIL_APP_PASSWORD")
STAFF_REGISTRATION_CODE = os.getenv("STAFF_REGISTRATION_CODE")

# -------Imports-------------------------------------------------
app=FastAPI()

# -------Session-------------------------------------------------
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="ums_session",
    https_only=False,
    same_site="lax",
    max_age=60*60*24
)

# -------Static Files-------------------------------------------------
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# -------Upload Folder-------------------------------------------------
UPLOAD_FOLDER=os.path.join(
    "static","uploads"
)
os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

# -------Jinja2 Templates-------------------------------------------------
templates = Jinja2Templates(
    directory="templates"
)

# -------Password-------------------------------------------------
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# -------Helper Function-------------------------------------------------
def redirect_to_dashboard(role: str, error: str = None, success: str = None):
    if role == "admin":
        url = "/admin-dashboard"
    elif role == "student":
        url = "/student-dashboard"
    elif role == "teacher":
        url = "/teacher-dashboard"
    else:
        url = "/login"

    if error:
        url += f"?error={error}"
    elif success:
        url += f"?success={success}"

    return RedirectResponse(url=url, status_code=303)


def is_valid_staff_code(submitted_code: str) -> bool:
    """
    Timing-safe comparison - avoids leaking info via response-time
    differences (a plain '==' comparison can theoretically be used
    to guess a secret character-by-character over many requests).
    """
    if not submitted_code or not STAFF_REGISTRATION_CODE:
        return False
    return secrets.compare_digest(submitted_code, STAFF_REGISTRATION_CODE)

# Send OTP Email
def send_otp_email(
    receiver_email: str,
    otp: int
):
    subject = "EduSphere Password Reset OTP"
    body = f"""
        Hello,
        Your OTP for resetting your EduSphere account password is:
        {otp}
        This OTP is valid for 2 minutes.
        If you did not request a password reset, please ignore this email.
        Thank you,
        EduSphere Team
"""

    message = MIMEMultipart()
    message["From"] = EMAIL_ADDRESS
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(
        MIMEText(
            body,
            "plain"
        ) )
    with smtplib.SMTP(

        "smtp.gmail.com",
        587
    ) as server:
        server.starttls()
        server.login(
            EMAIL_ADDRESS,
            EMAIL_APP_PASSWORD
        )
        server.send_message(message)


ALLOWED_ROLES = {"student", "teacher", "admin"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# -------Pages-------------------------------------------------
# -------------------------------------------------------------


# -------Home-------------------------------------------------
@app.get("/")
def home(req:Request):
    return templates.TemplateResponse(
        name="index.html",
        request=req
    )


# -------Login-------------------------------------------------
@app.get("/login")
def login_page(req:Request, error: str=None, success:str=None):

    existing_user = None
    if "user_id" in req.session:
        user = collections.find_one({"_id": ObjectId(req.session["user_id"])})
        if not user:
            req.session.clear()
        else:
            existing_user = user

    return templates.TemplateResponse(
        name="login.html",
        context={"request":req,"error":error,"success":success, "existing_user":existing_user},
        request=req
    )

@app.get("/already-login")
def already_login(
    req:Request,
     error: str=None,
     success:str=None
):
    
    if "user_id" in req.session:
        user=collections.find_one({"_id":ObjectId(req.session["user_id"])})
        if not user:
            # agar user DB se delete ho chuka ho but session abhi bhi purana hai
            req.session.clear()
        elif req.session["role"]=="admin":
            return RedirectResponse(url="/admin-dashboard", status_code=303)
        elif req.session["role"]=="student":
            return RedirectResponse(url="/student-dashboard", status_code=303)
        elif req.session["role"]=="teacher":
            return RedirectResponse(url="/teacher-dashboard", status_code=303)
        else:
            print(f"Unexpected role for user {user['_id']}: {user['role']}")
            req.session.clear()
            
    return templates.TemplateResponse(
        name="login.html",
        context={"request":req,"error":error,"success":success},
        request=req
    )

@app.post("/login")
def login(
    req:Request,
    email:str=Form(...),
    password:str=Form(...),
):
    user=collections.find_one({"email":email})
    if not user:
        return RedirectResponse(
            url="/login?error=User Not Registered",
            status_code=303
        )
    password_matched=pwd_context.verify(password,user["password"])
    if not password_matched:
        return RedirectResponse(
            url="/login?error=Wrong Password",
            status_code=303
        )
    role=user["role"]
    id=user["_id"]
    req.session["user_id"]=str(id)
    req.session["role"]=role
    return redirect_to_dashboard(role)
# -------Admin-Dashboard-------------------------------------------------
@app.get("/admin-dashboard")
def admin_page(
    req: Request,
    error: str = None,
    success: str = None
):
    if "user_id" not in req.session:
        return RedirectResponse(
            url="/login?error=Session Expired",
            status_code=303
        )
    if req.session["role"] != "admin":
        return redirect_to_dashboard(req.session["role"])

    user = collections.find_one({"_id": ObjectId(req.session["user_id"])})
    return templates.TemplateResponse(
        request=req,
        name="admin_dashboard.html",
        context={
            "request": req,
            "user": user,
            "error": error,
            "success": success
        }
    )

# -------Student-Dashboard-------------------------------------------------
@app.get("/student-dashboard")
def student_page(
    req: Request,
    error: str = None,
    success: str = None
):
    if "user_id" not in req.session:
        return RedirectResponse(
            url="/login?error=Session Expired",
            status_code=303
        )
    if req.session["role"] != "student":
        return redirect_to_dashboard(req.session["role"])

    user = collections.find_one({"_id": ObjectId(req.session["user_id"])})
    return templates.TemplateResponse(
        request=req,
        name="student_dashboard.html",
        context={
            "request": req,
            "user": user,
            "error": error,
            "success": success
        }
    )

# -------Teacher-Dashboard-------------------------------------------------
@app.get("/teacher-dashboard")
def teacher_page(
    req: Request,
    error: str = None,
    success: str = None
):
    if "user_id" not in req.session:
        return RedirectResponse(
            url="/login?error=Session Expired",
            status_code=303
        )
    if req.session["role"] != "teacher":
        return redirect_to_dashboard(req.session["role"])

    user = collections.find_one({"_id": ObjectId(req.session["user_id"])})
    return templates.TemplateResponse(
        request=req,
        name="teacher_dashboard.html",
        context={
            "request": req,
            "user": user,
            "error": error,
            "success": success
        }
    )


# -------Register-------------------------------------------------
@app.get("/register")
def registration_page(
    req:Request,
    error:str=None
):
    existing_user = None
    if "user_id" in req.session:
        user = collections.find_one({"_id": ObjectId(req.session["user_id"])})
        if not user:
            req.session.clear()
        else:
            existing_user = user
        
    return templates.TemplateResponse(
        name="register.html",
        context={"request":req,"error":error, "existing_user":existing_user},
        request=req
    )

@app.post("/register")
def register(
    req:Request,
    profile_image: UploadFile=File(...),
    role:str=Form(...),
    full_name:str=Form(...),
    email:str=Form(...),
    mobile:str=Form(...),
    password:str=Form(...),
    confirm_password:str=Form(...),
    department:str=Form(...),
    security_code: str = Form(""),
    terms:str=Form(...)
):
    email = email.strip().lower()

    if not profile_image.filename:
        return RedirectResponse(
            url="/register?error=Please Upload The Profile Image To Proceed",
            status_code=303
        )
    
    if role not in ALLOWED_ROLES:
        role = "student"

    if terms != "on":
        return RedirectResponse(url="/register?error=You Must Accept The Terms", status_code=303)

    if password!=confirm_password:
        return RedirectResponse(
            url="/register?error=Passwoerds Do Not Match",
            status_code=303
        )
    
    existing_user=collections.find_one({"email":email})
    if existing_user:
        return RedirectResponse(
            url="/register?error=Email Already Exists",
            status_code=303
        )

    if role in {"teacher", "admin"} and not is_valid_staff_code(security_code):
        return RedirectResponse(
            url="/register?error=Invalid Staff Registration Code",
            status_code=303
        )

    file_extension = os.path.splitext(
        profile_image.filename
    )[1]
    if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
        return RedirectResponse(url="/register?error=Invalid Image Format", status_code=303)
    
    unique_filename = (
        f"{uuid.uuid4().hex}"
        f"{file_extension}"
    )
    image_path = os.path.join(
        UPLOAD_FOLDER,
        unique_filename
    )
    with open(
        image_path,
        "wb"
    ) as buffer:
        shutil.copyfileobj(
            profile_image.file,
            buffer
        )
    
    final_password=pwd_context.hash(password)

    user={
        "role":role,
        "full_name":full_name,
        "email":email,
        "mobile":mobile,
        "password":final_password,
        "department":department,
        "profile_image":unique_filename
    }
    collections.insert_one(user)
    req.session.clear()
    return RedirectResponse(
        url="/login?success=Registration Successful",
        status_code=303
    )

# -------Logout-------------------------------------------------
@app.get("/logout")
def logout(req:Request):
    req.session.clear()
    return RedirectResponse(
        url="/login",
        status_code=303
    )


# -------Update Details-------------------------------------------------
@app.get("/change-details")
def change_details(req: Request):
    if "user_id" not in req.session:
        return RedirectResponse("/login?error=Session Expired", status_code=303)
    user_id = ObjectId(req.session["user_id"])
    user = collections.find_one({"_id": user_id})
    return templates.TemplateResponse(
        name="dashboard.html",
        context={
            "request": req,
            "user": user
        },
        request=req
    )
@app.post("/change-details")
def change_details(
    req: Request,
    full_name: str = Form(""),
    email: str = Form(""),
    mobile: str = Form("")
):
    if "user_id" not in req.session:
        return RedirectResponse("/login?error=Session Expired", status_code=303)

    user_id = ObjectId(req.session["user_id"])
    email = email.strip().lower()
    role = req.session.get("role")

    if collections.find_one({"email": email, "_id": {"$ne": user_id}}):
        user = collections.find_one({"_id": user_id})

        if role == "admin":
            template_name = "admin_dashboard.html"
        elif role == "teacher":
            template_name = "teacher_dashboard.html"
        elif role == "student":
            template_name = "student_dashboard.html"
        else:
            req.session.clear()
            return RedirectResponse("/login?error=Session Expired", status_code=303)

        return templates.TemplateResponse(
            template_name,
            {"request": req, "user": user, "error": "Email already exists."}
        )
    collections.update_one(
        {"_id": user_id},
        {"$set": {"full_name": full_name, "email": email, "mobile": mobile}}
    )

    return redirect_to_dashboard(req.session["role"])

# -------Update Details-------------------------------------------------
@app.get("/student-dashboard/profile")
def profile_page(req:Request, error: str=None, success:str=None):
    if "user_id" not in req.session:
        return RedirectResponse("/login?error=Session Expired", status_code=303)
    user_id = ObjectId(req.session["user_id"])
    user = collections.find_one({"_id": user_id})
    return templates.TemplateResponse(
        name="profile.html",
        context={
            "user":user,
            "error":error,
            "success":success
        },
        request=req
    )
@app.get("/admin-dashboard/profile")
def profile_page(req:Request, error: str=None, success:str=None):
    if "user_id" not in req.session:
        return RedirectResponse("/login?error=Session Expired", status_code=303)
    user_id = ObjectId(req.session["user_id"])
    user = collections.find_one({"_id": user_id})
    return templates.TemplateResponse(
        name="profile.html",
        context={
            "user":user,
            "error":error,
            "success":success
        },
        request=req
    )
@app.get("/teacher-dashboard/profile")
def profile_page(req:Request, error: str=None, success:str=None):
    if "user_id" not in req.session:
        return RedirectResponse("/login?error=Session Expired", status_code=303)
    user_id = ObjectId(req.session["user_id"])
    user = collections.find_one({"_id": user_id})
    return templates.TemplateResponse(
        name="profile.html",
        context={
            "user":user,
            "error":error,
            "success":success
        },
        request=req
    )




# @app.get("/admin-dashboard/change-password")
# def forgot_password_page(req: Request, error:str=None,success:str=None):
#     user=collections.find_one(req.session["user_id"])
#     if not user:
#         return templates.TemplateResponse(
#             request=req,
#             name="forgot_password.html",
#             context={"request":req,"error": error,"success": success}
#         )
        
#     else:
#         return templates.TemplateResponse(
#                     request=req,
#                     name="forgot_password.html",
#                     context={"request":req,"error": error,"success": success}
#                 )


    
# =========================================================
#  CHANGE PASSWORD — logged-in user, via dashboard OTP modal
#  Generic for admin/student/teacher (not role-specific)
# =========================================================
@app.post("/send-password-otp")
def send_password_otp(req: Request):
    if "user_id" not in req.session:
        return JSONResponse({"error": "Session Expired"}, status_code=401)

    user = collections.find_one({"_id": ObjectId(req.session["user_id"])})
    if not user:
        req.session.clear()
        return JSONResponse({"error": "Session Expired"}, status_code=401)

    otp = random.randint(100000, 999999)
    print(otp)  # dev-only, remove before production
    req.session["password_otp"] = str(otp)
    req.session["password_otp_expiry"] = (datetime.now() + timedelta(minutes=2)).isoformat()
    req.session["password_otp_verified"] = False

    try:
        send_otp_email(user["email"], otp)
    except Exception as e:
        print(f"[OTP EMAIL ERROR] {e}")
        return JSONResponse({"error": "Failed to send OTP. Try again."}, status_code=500)

    return JSONResponse({"success": True, "message": "OTP sent to your email"})


@app.post("/verify-password-otp")
def verify_password_otp(req: Request, otp: str = Form(...)):
    if "user_id" not in req.session:
        return JSONResponse({"error": "Session Expired"}, status_code=401)

    stored_otp = req.session.get("password_otp")
    expiry_str = req.session.get("password_otp_expiry")

    if not stored_otp or not expiry_str:
        return JSONResponse({"error": "No OTP requested. Please request one first."}, status_code=400)

    if datetime.now() > datetime.fromisoformat(expiry_str):
        req.session.pop("password_otp", None)
        req.session.pop("password_otp_expiry", None)
        return JSONResponse({"error": "OTP expired. Please request a new one."}, status_code=400)

    if not secrets.compare_digest(otp, stored_otp):
        return JSONResponse({"error": "Incorrect OTP."}, status_code=400)

    req.session["password_otp_verified"] = True
    return JSONResponse({"success": True, "message": "OTP verified."})
   

@app.post("/change-password")
def change_password_dashboard(
    req: Request,
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    if "user_id" not in req.session:
        return RedirectResponse("/login?error=Session Expired", status_code=303)

    user = collections.find_one({"_id": ObjectId(req.session["user_id"])})
    if not user:
        req.session.clear()
        return RedirectResponse("/login?error=Session Expired", status_code=303)

    if not req.session.get("password_otp_verified"):
        return redirect_to_dashboard(req.session["role"], error="Please verify OTP before changing password")

    if new_password != confirm_password:
        return redirect_to_dashboard(req.session["role"], error="Passwords do not match")

    hashed = pwd_context.hash(new_password)
    collections.update_one({"_id": user["_id"]}, {"$set": {"password": hashed}})

    req.session.pop("password_otp", None)
    req.session.pop("password_otp_expiry", None)
    req.session.pop("password_otp_verified", None)
    req.session.clear()
    return RedirectResponse(
        url="/login?success=Password Updated Successfully",
        status_code=303
    )
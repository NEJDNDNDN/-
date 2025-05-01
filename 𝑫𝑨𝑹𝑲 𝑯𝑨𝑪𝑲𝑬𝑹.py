import requests
import time
from termcolor import colored
import webbrowser

# حقوق الأداة
def show_rights():
    print(colored("𝐃𝐀𝐑𝐊 𝐇𝐀𝐂𝐊𝐄𝐑 - الأداة لزيادة مشاهدات تيكتوك", "cyan"))
    print(colored("تأكد من استخدام الأداة في الأمور القانونية فقط!", "yellow"))
    print(colored("جميع الحقوق محفوظة", "green"))
    print(colored("انضم إلى قناتي على تيليجرام للحصول على المزيد من الأدوات والمساعدات: https://t.me/+PFbp1Ayc_1I3ZTFk", "blue"))

# تحويل المستخدم للقناة
def redirect_to_channel():
    print(colored("الرجاء الانضمام إلى القناة على تيليجرام قبل متابعة استخدام الأداة...", "magenta"))
    time.sleep(2)
    webbrowser.open("https://t.me/+PFbp1Ayc_1I3ZTFk")  # فتح القناة

# دالة لزيادة المشاهدات
def increase_views(video_url, views_count):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    for i in range(views_count):
        response = requests.get(video_url, headers=headers)
        if response.status_code == 200:
            print(f"تم إضافة مشاهدة {i+1}/{views_count}")
        else:
            print("حدث خطأ أثناء زيادة المشاهدات.")
        time.sleep(2)  # تأخير بين المشاهدات

# واجهة المستخدم
def user_interface():
    print(colored("مرحبًا بك في أداة زيادة مشاهدات تيكتوك", "cyan"))
    show_rights()
    redirect_to_channel()  # تحويل المستخدم إلى القناة
    
    video_url = input("أدخل رابط الفيديو على تيكتوك: ")
    try:
        views_count = int(input("أدخل عدد المشاهدات التي تريد إضافتها: "))
        increase_views(video_url, views_count)
    except ValueError:
        print(colored("يرجى إدخال عدد صحيح للمشاهدات.", "red"))

if __name__ == "__main__":
    user_interface()

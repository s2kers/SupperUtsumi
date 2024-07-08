from django.utils import timezone
import re

from django.shortcuts import render, redirect
from datetime import date, datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .models import Employee, Shiiregyosha, Patient, Medicine, Treatment
from django.shortcuts import render, get_object_or_404, redirect


def login_view(request):
    if request.method == 'POST':
        empid = request.POST['empid']
        password = request.POST["password"]
        if not empid or not password:
            messages.error(request, '空白の欄があります')
        else:
            try:
                employee = Employee.objects.get(empid=empid)
            except Employee.DoesNotExist:
                messages.error(request, "ユーザIDもしくはパスワードが違います")
                return render(request, 'index.html')
            if employee.emppasswd == password:  # Here, normally you should hash and verify the password
                request.session['empid'] = employee.empid
                if employee.emprole == 0:
                    return render(request, 'kada1/admin/admin.html')
                elif employee.emprole == 1:
                    return render(request, 'Kada1/uketuke/reception.html', {'empid': empid})
                elif employee.emprole == 2:
                    return render(request, 'Kada1/uketuke/docter.html', {'empid': empid})
            else:
                messages.error(request, "ユーザIDもしくはパスワードが違います")
                return render(request, 'index.html')
    return render(request, 'index.html')


def logout_view(request):
    logout(request)
    return redirect('Kadai1/L100/Login.html')


def admin_dashboard(request):
    return render(request, 'Kada1/admin/admin.html')


def reception_dashboard(request):
    return render(request, 'Kada1/uketuke/reception.html')


def doctor_dashboard(request):
    return render(request, 'Kada1/uketuke/Docter.html')


def register_employee(request):
    if request.method == 'POST':
        empid = request.POST.get('empid')
        empfname = request.POST.get('empfname')
        emplname = request.POST.get('emplname')
        emppasswd = request.POST.get('emppasswd')
        confirmemppasswd = request.POST.get('confirmemppasswd')
        emprole = request.POST.get('emprole')
        if not empid or not empfname or not emplname or not emppasswd or not confirmemppasswd or not emprole:
            messages.error(request, '空白の欄があります')
        elif Employee.objects.filter(empid=empid).exists():
            messages.error(request, 'このユーザーIDは既に存在します。')
        elif emppasswd != confirmemppasswd:
            messages.error(request, '入力したパスワードが一致しません')
        elif emprole == '0':
            messages.error(request, '管理者を登録することはできません')
        elif emprole != '1' and emprole != '2':
            messages.error(request, '役職は指定した数字を入力してください')
        else:
            employee = Employee(empid=empid, empfname=empfname, emplname=emplname, emppasswd=emppasswd, emprole=emprole)
            employee.save()
            return render(request, 'Kada1/admin/register_success.html')

    return render(request, 'Kada1/admin/Registeremployee.html')


def employee_list(request):
    if request.method == 'GET':
        employees = Employee.objects.all()
        return render(request, 'kada1/admin/employeelist.html', {'employees': employees})


def employee_kensaku(request):
    query = request.GET.get('query')
    if query:
        employees = Employee.objects.filter(empid__icontains=query)
        if not employees:
            messages.error(request, '該当する従業員が見つかりませんでした')
    else:
        employees = Employee.objects.all()
    return render(request, 'kada1/admin/shiirelist.html', {'employees': employees, 'query': query})


def update_employee(request, empid):
    employee = get_object_or_404(Employee, empid=empid)
    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_new_password = request.POST['confirm_new_password']
        if not new_password or not confirm_new_password:
            messages.error(request, '空白の欄があります')
            return render(request, 'kada1/admin/passwordupdate.html', {'employee': employee})
        elif employee.emppasswd == new_password or employee.emppasswd == confirm_new_password:
            messages.error(request, '古いパスワードと同じパスワードが入力されてます')
            return render(request, 'kada1/admin/passwordupdate.html', {'employee': employee})
        elif new_password != confirm_new_password:
            messages.error(request, 'パスワードが一致しません')
            return render(request, 'kada1/admin/passwordupdate.html', {'employee': employee})
        return render(request, 'kada1/admin/confirmpassword.html', {'employee': employee, 'new_password': new_password})
    return render(request, 'kada1/admin/passwordupdate.html', {'employee': employee})


def confirmupdate(request):
    if request.method == 'POST':
        empid = request.POST.get('empid')
        new_password = request.POST.get("new_password")
        employee = Employee.objects.get(empid=empid)
        employee.emppasswd = new_password
        employee.save()
    return render(request, 'kada1/admin/successupdate.html')


def shiire_list(request):
    query = request.GET.get('q')
    if query:
        shiires = Shiiregyosha.objects.filter(shiireaddres__icontains=query)
        if not shiires:
            messages.error(request, '該当する病院が見つかりませんでした')
    else:
        shiires = Shiiregyosha.objects.all()
    return render(request, 'kada1/admin/shiirelist.html', {'shiires': shiires, 'query': query})


def tabyouin_register(request):
    if request.method == 'POST':
        tabyouinid = request.POST.get('tabyouinid')
        tabyouinmei = request.POST.get('tabyouinmei')
        abyouinaddres = request.POST.get('abyouinaddres')
        tabyouintel = request.POST.get('tabyouintel')
        abyouinshihonkin = request.POST.get('abyouinshihonkin')
        kyukyu = request.POST.get('kyukyu')
        if not tabyouinid or not tabyouinmei or not abyouinaddres or not tabyouintel or not abyouinshihonkin or not kyukyu:
            messages.error(request, '空白の欄があります')
        elif Shiiregyosha.objects.filter(tabyouinid=tabyouinid).exists():
            messages.error(request, 'この病院はすでに登録されています。')
        elif kyukyu != '0' and kyukyu != '1':
            messages.error(request, '救急対応は指定された数字を入力してください')
        elif not re.match(r'^[0-9()-]+$', tabyouintel):
            messages.error(request, '電話番号は半角数字、括弧、ハイフンのみを含むことができます')
            return render(request, 'Kada1/tabyo/tabyouin_register.html')
        elif len(tabyouintel) < 11 or len(tabyouintel) > 15:
            messages.error(request, '電話番号は11桁から15桁でなければなりません')
            return render(request, 'Kada1/tabyo/tabyouin_register.html')
        else:
            tabyouin = Shiiregyosha(tabyouinid=tabyouinid, tabyouinmei=tabyouinmei, abyouinaddres=abyouinaddres,
                                    tabyouintel=tabyouintel, abyouinshihonkin=abyouinshihonkin, kyukyu=kyukyu)
            tabyouin.save()
            return render(request, 'Kada1/tabyo/tabyouin_success.html')
    return render(request, 'Kada1/tabyo/tabyouin_register.html')


def patient_register(request):
    if request.method == 'POST':
        patid = request.POST.get('patid')
        patfname = request.POST.get('patfname')
        patlname = request.POST.get('patlname')
        hokenmei = request.POST.get('hokenmei')
        hokenexp = request.POST.get('hokenexp')
        if not patid or not patfname or not patlname or not hokenmei or not hokenexp:
            messages.error(request, ' 空白の欄があります')
        elif Patient.objects.filter(patid=patid).exists():
            messages.error(request, 'この患者IDはすでに登録されています。')
        elif not len(hokenmei) == 10:
            messages.error(request, '保険証記号番号は10桁である必要があります。')
        else:
            patient = Patient(patid=patid, patfname=patfname, patlname=patlname, hokenmei=hokenmei, hokenexp=hokenexp)
            patient.save()
            return redirect('patient_success')
    return render(request, 'Kada1/pat/patient_register.html')


def patient_success(request):
    return render(request, 'Kada1/pat/patient_success.html')


def string_to_date(date_string: str) -> date:
    try:
        # 日付文字列をdatetimeオブジェクトに
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        # datetimeオブジェクトをdateオブジェクトに変換
        return date_obj.date()
    except ValueError:
        # 日付文字列のフォーマットが不正な場合
        raise ValueError("Incorrect date format, should be YYYY-MM-DD")


def update_hoken(request, patid):
    patient = get_object_or_404(Patient, patid=patid)
    if request.method == 'POST':
        new_hokenmei = request.POST['new_hokenmei']
        new_hokenexp = request.POST['new_hokenexp']
        new_hokenexp_date = string_to_date(date_string=new_hokenexp)
        if patient.hokenexp > new_hokenexp_date:
            messages.error(request, '現在の有効期限より古い日付での更新はできません')
        elif patient.hokenexp == new_hokenexp_date:
            messages.error(request, '現在の有効期限と同じ日付になっています')
        else:
            if not new_hokenmei:
                new_hokenmei = patient.hokenmei
            elif not len(new_hokenmei) == 10:
                messages.error(request, '保険証記号番号は10桁である必要があります')
                return render(request, 'Kada1/pat/update_hoken.html', {'patient': patient})
            return render(request, 'Kada1/pat/confirm_update_hoken.html',
                          {'patient': patient, 'new_hokenmei': new_hokenmei, 'new_hokenexp': new_hokenexp})
    return render(request, 'Kada1/pat/update_hoken.html', {'patient': patient})


def confirm_update_hoken(request):
    if request.method == 'POST':
        patid = request.POST.get('patid')
        new_hokenmei = request.POST.get("new_hokenmei")
        new_hokenexp = request.POST.get("new_hokenexp")
        patient = Patient.objects.get(patid=patid)
        patient.hokenmei = new_hokenmei
        patient.hokenexp = new_hokenexp
        patient.save()
    return render(request, 'Kada1/pat/success_update_hoken.html')


def patient_kensaku(request):
    query = request.GET.get('query')
    if query:
        patients = Patient.objects.filter(patlname_conteins=query)
        if not patients:
            patients = Patient.objects.filter(patfname_conteins=query)
            if not patients:
                messages.error(request, '該当する患者が見つかりませんでした')
    else:
        patients = Patient.objects.all()
    return render(request, 'kada1/uketuke/patient_list.html', {'patients': patients, 'query': query})


def doctor_kensaku(request):
    query = request.GET.get('query')
    if query:
        patients = Patient.objects.filter(patlname=query)
        if not patients:
            patients = Patient.objects.filter(patfname=query)
            if not patients:
                messages.error(request, '該当する患者が見つかりませんでした')
    else:
        patients = Patient.objects.all()
    return render(request, 'Kada1/pat/Docter_patient_list.html', {'patients': patients, 'query': query})


def treatment_list(request, patid):
    patient = get_object_or_404(Patient, patid=patid)
    medicines = Medicine.objects.all()
    treatments = request.session.get(f'treatments_{patid}', [])

    # 薬剤名を追加
    treatment_details = []
    for index, pres in enumerate(treatments):
        medicine = get_object_or_404(Medicine, medicineid=pres['medicine'])
        treatment_details.append({
            'index': index,
            'medicinename': medicine.medicinename,
            'dosage': pres['dosage']
        })

    return render(request, 'Kada1/docter1/touyo2.html', {
        'patient': patient,
        'medicines': medicines,
        'treatments': treatment_details,
    })


def add_prescription(request, patid):
    medicine_id = request.POST.get('medicine')
    dosage = request.POST.get('dosage')
    if not dosage:
        messages.error(request, '数量が空欄になっています')
        return render(request, 'Kada1/errorpage.html')

    try:
        dosage = int(dosage)
    except ValueError:
        messages.error(request, '数量は数字を入力してください')
        return render(request, 'Kada1/errorpage.html')

    if dosage <= 0:
        messages.error(request, '数量は正の数字を入力してください')
        return render(request, 'Kada1/errorpage.html')

    # セッションから治療リストを取得（存在しない場合は初期化）
    treatments = request.session.get(f'treatments_{patid}', [])

    # 薬剤が既に存在するかどうか確認
    found = False
    for pres in treatments:
        if pres['medicine'] == medicine_id:
            pres['dosage'] += dosage
            found = True
            break

    # 存在しなければ新しく追加
    if not found:
        treatments.append({
            'medicine': medicine_id,
            'dosage': dosage
        })

    request.session[f'treatments_{patid}'] = treatments
    return redirect('treatment_list', patid=patid)


def delete_prescription(request, patid, index):
    index = int(index)
    treatments = request.session.get(f'treatments_{patid}', [])
    if 0 <= index < len(treatments):
        del treatments[index]
    request.session[f'treatments_{patid}'] = treatments
    return redirect('treatment_list', patid=patid)


def confirm_prescription(request, patid):
    if request.method == 'POST':
        treatments = request.session.get(f'treatments_{patid}', [])
        patient = get_object_or_404(Patient, patid=patid)
        if not treatments:
            return redirect('treatment_list', patid=patid)
        for pres in treatments:
            medicine = get_object_or_404(Medicine, medicineid=pres['medicine'])
            Treatment.objects.create(
                patient=patient,
                medicine=medicine,
                dosage=pres['dosage'],
                created_at=timezone.now()
            )
        del request.session[f'treatments_{patid}']
        return render(request, 'Kada1/docter1/touyo3.html')
    else:
        treatments = request.session.get(f'treatments_{patid}', [])
        medicine_objects = {m.medicineid: m for m in Medicine.objects.all()}
        context = {
            'patient': get_object_or_404(Patient, patid=patid),
            'treatments': treatments,
            'medicines': medicine_objects
        }
        return render(request, 'Kada1/docter1/touyo2.html', context)


def patient_search(request):
    query = request.GET.get('query')
    if query:
        patients = Patient.objects.filter(patid=query)
        if not patients:
            messages.error(request, '該当する患者が見つかりませんでした')
    else:
        patients = Patient.objects.all()
    return render(request, 'Kada1/docter1/touyo4.html', {'patients': patients, 'query': query})


def patient_prescriptions(request, patid):
    patient = get_object_or_404(Patient, patid=patid)

    treatments = Treatment.objects.filter(patient=patient).select_related('medicine')
    if not treatments:
        messages.error(request, 'この患者は処置されていません')
    return render(request, 'Kada1/docter1/touyo5.html', {'patient': patient, 'treatments': treatments})


def shiiregyosha_register(request):
    if request.method == 'POST':
        shiireid = request.POST.get('shiireid')
        shiiremei = request.POST.get('shiiremei')
        shiireaddress = request.POST.get('shiireaddress')
        shiiretel = request.POST.get('shiiretel')
        shihonkin = request.POST.get('shihonkin')
        nouki = request.POST.get('nouki')
        if not shiireid or not shiiremei or not shiireaddress or not shiiretel or not shihonkin or not nouki:
            messages.error(request, '空白の欄があります')
        else:
            shiiregyosha = Shiiregyosha(shiireid=shiireid, shiiremei=shiiremei, shiireaddress=shiireaddress,
                                        shiiretel=shiiretel, shihonkin=shihonkin, nouki=nouki)
            shiiregyosha.save()
            return render(request, 'kada1/admin/shiiregyosha_register_success.html')
        return render(request, 'kada1/admin/shiiregyosha_register.html')
    return render(request, 'kada1/admin/shiiregyosha_register.html')

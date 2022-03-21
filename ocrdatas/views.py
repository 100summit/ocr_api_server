import dataclasses
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from rest_framework.parsers import JSONParser
from .models import OcrDatas
from .serializers import OcrDataSerializer
from dataclasses import dataclass
from dataclasses_json import dataclass_json

# Create your views here.
import numpy as np
import time
import os
import sqlite3
from data import ocrResult, ocrData, chevrolet, response_success
import cv2

subscription_key = "5b2825ec3afd4b11b15886abcdf61acc"
endpoint = "https://seans.cognitiveservices.azure.com/"

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))



def createDB(array):
    ocrResultArray = []
    conn = sqlite3.connect("carManager.db", isolation_level=None)

    c = conn.cursor()

    # c.execute("CREATE TABLE IF NOT EXISTS CHEVROLET (id integer PRIMARY KEY, data string)")
    #
    # c.execute("INSERT INTO CHEVROLET VALUES(1, '기본가격')")

    i = 0
    itemX = 0
    ok = False
    c.execute("SELECT data FROM CHEVROLET WHERE id<12")


    cFetchall = c.fetchall()

    for row in cFetchall:
        for ff in array:
            if ff.text == row[0]:
                base = (int(ff.y1) + int(ff.y2)) / 2
                while 5:
                    for gg in array:
                        if ff.text != gg.text and abs(base - ((int(gg.y1) + int(gg.y2)) / 2)) <= i and int(ff.x2) < int(gg.x1):

                            if str(gg.text.replace(".", ",")).__contains__("할인금액"):
                                continue

                            if ff.text == cFetchall[9][0] and int(gg.x1) == itemX:
                                continue

                            if ff.text == cFetchall[8][0]:
                                itemX = int(gg.x1)

                            ocrResultArray.append(ocrResult.Data(ff.text, gg.text.replace(".", ",")))
                            ok = True

                    if ok:
                        ok = False
                        i = 0
                        break
                    else:
                        i = i + 1
    conn.close()

    for aa in ocrResultArray:
        print(aa.word + " = " + aa.result)

    return saveOcrData(ocrResultArray, cFetchall)


def saveOcrData(array, cAll):
    returnChevrolet = chevrolet.Data(basicPrice="", optionPrice="", consignmentPrice="", acquisitionTax="", bond="", proof_license="", registrationFee="", paymentMethod="", downPayment="", deliveryFee="", total="")

    for row in array:
        if row.word == cAll[0][0]:
            returnChevrolet.basicPrice = row.result
        elif row.word == cAll[1][0]:
            returnChevrolet.optionPrice = row.result
        elif row.word == cAll[2][0]:
            returnChevrolet.consignmentPrice = row.result
        elif row.word == cAll[3][0]:
            returnChevrolet.acquisitionTax = row.result
        elif row.word == cAll[4][0]:
            returnChevrolet.bond = row.result
        elif row.word == cAll[5][0]:
            returnChevrolet.proof_license = row.result
        elif row.word == cAll[6][0]:
            returnChevrolet.registrationFee = row.result
        elif row.word == cAll[7][0]:
            returnChevrolet.paymentMethod = row.result
        elif row.word == cAll[8][0]:
            returnChevrolet.downPayment = row.result
        elif row.word == cAll[9][0]:
            returnChevrolet.deliveryFee = row.result
        elif row.word == cAll[10][0]:
            returnChevrolet.total = row.result


    return returnChevrolet


def ocrStart(resource):
    # 이미지 불러오기
    src = cv2.imdecode(np.fromstring(resource, np.uint8), cv2.IMREAD_COLOR)
    # src = cv2.rotate(cv2.imdecode(np.fromstring(resource, np.uint8), cv2.IMREAD_COLOR), cv2.ROTATE_90_CLOCKWISE)

    # src = cv2.imread("C:/Users/rlaxo/PycharmProjects/pythonProject/images/realSample.jpg")

    # 출력 영상 설정
    dw, dh = 1200, 1500
    # dw, dh = 2480, 3508
    srcQuad = np.array([[0, 0], [0, 0], [0, 0], [0, 0]], np.float32)
    dstQuad = np.array([[0, 0], [0, dh], [dw, dh], [dw, 0]], np.float32)
    dst = np.zeros((dh, dw), np.uint8)

    # 입력 영상 전처리
    src_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    _, src_bin = cv2.threshold(src_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # 외곽선 검출 및 명함 검출
    contours, _ = cv2.findContours(src_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    cpy = src.copy()
    for pts in contours:
        # 너무 작은 객체는 무시
        if cv2.contourArea(pts) < 1000:
            continue

        # 외곽선 근사화
        approx = cv2.approxPolyDP(pts, cv2.arcLength(pts, True) * 0.02, True)

        # 컨벡스가 아니고, 사각형이 아니면 무시
        if not cv2.isContourConvex(approx) or len(approx) != 4:
            continue

        cv2.polylines(cpy, [approx], True, (0, 255, 0), 2, cv2.LINE_AA)
        srcQuad = reorderPts(approx.reshape(4, 2).astype(np.float32))

    pers = cv2.getPerspectiveTransform(srcQuad, dstQuad)
    dst = cv2.warpPerspective(src, pers, (dw, dh))

    dst_gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)

    # read_image_path = os.path.join ("C:/Users/rlaxo/PycharmProjects/pythonProject/images/Normal.jpg")
    # img = cv2.imread("C:/Users/rlaxo/PycharmProjects/pythonProject/images/Normal.jpg")
    # sample = cv2.resize(img, (900, 1200))
    # read_image = open(sample, "rb")

    image_path = "{}_resized.jpg".format("image")
    cv2.imwrite(image_path, dst_gray)
    read_image_path = os.path.join(image_path)
    read_image = open(read_image_path, "rb")

    # cv2.imshow("sample", dst_gray)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # root.mainloop()

    return azureOCR(read_image)


def reorderPts(pts):  # 꼭지점 순서 정렬
    idx = np.lexsort((pts[:, 1], pts[:, 0]))  # 칼럼0 -> 칼럼1 순으로 정렬한 인덱스를 반환
    pts = pts[idx]  # x좌표로 정렬

    if pts[0, 1] > pts[1, 1]:
        pts[[0, 1]] = pts[[1, 0]]  # 스와핑

    if pts[2, 1] < pts[3, 1]:
        pts[[2, 3]] = pts[[3, 2]]  # 스와핑

    return pts


def azureOCR(custom_image):
    ocrArray = []

    ''' 이미지 파일로 API 호출
    :param image:
    '''
    read_response = computervision_client.read_in_stream(custom_image, raw=True)

    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for it to retrieve the results
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # root = tk.Tk()
    # canvas = tk.Canvas(root, width=1000, height=1300, bg="SpringGreen2")
    # canvas.pack()
    # Print the detected text, line by line

    # rectImage = original.copy()
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                if str(line.text.replace(" ", "")).__contains__("계약금(a)/인도금(b)"):
                    ocrArray.append(
                        ocrData.Data("계약금(a)", line.bounding_box[0], line.bounding_box[1],
                                     line.bounding_box[4],
                                     line.bounding_box[5]))

                    ocrArray.append(
                            ocrData.Data("인도금(b)", line.bounding_box[0], line.bounding_box[1],
                                     line.bounding_box[4],
                                     line.bounding_box[5]))

                else:
                    ocrArray.append(
                        ocrData.Data(line.text.replace(" ", ""), line.bounding_box[0], line.bounding_box[1],
                                 line.bounding_box[4],
                                 line.bounding_box[5]))
                # print(line)
                # tk.Label(root, text=line.text, font=("Arial", 8)).place(x=line.bounding_box[0], y=line.bounding_box[1])
                # cv2.rectangle(rectImage, (int(line.bounding_box[0]), int(line.bounding_box[1])),
                #               (int(line.bounding_box[4]), int(line.bounding_box[5])), (0, 255, 0), 1)

    # cv2.imshow("sample", rectImage)
    # key = cv2.waitKey(0)
    # print(key)
    # cv2.destroyAllWindows()

    # root.mainloop()
    # print(ocrArray)
    return createDB(ocrArray)


@csrf_exempt
def ocrdata_list(request):
    if request.method == 'GET':
        query_set = OcrDatas.objects.all()
        serializers = OcrDataSerializer(query_set, many=True)
        return JsonResponse(serializers.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = OcrDataSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def ttest(request):
    if request.method == 'GET':
        # data = ocrStart(resource)
        #
        # query = response_success.Data(result=None, createAt=None, data=data)
        #
        # query_set = query.to_dict()

        return JsonResponse("query_set", safe=False)



@csrf_exempt
def ocr_upload(request):
    if request.method == 'POST':

        resource = request.FILES['RESOURCE']
        com = request.POST['COM']

        # print(resource.read())

        data = ocrStart(resource.read())

        query = response_success.Data(result=None, createAt=None, data=data)

        query_set = query.to_dict()

        return JsonResponse(query_set, safe=False)
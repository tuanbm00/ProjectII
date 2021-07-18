import datetime
import sys
import math
from tkinter import *
from tkinter.ttk import *
from functools import partial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import matplotlib.legend
from pandas import *
from datetime import *
import numpy as np
from tkinter import filedialog
from ortools.linear_solver import pywraplp
from tkinter import messagebox


# đối tượng lưu trữ thông tin trạng thái máy trong khoảng thời gian đơn hàng
class Machine:
    def __init__(self, start, end):
        self.timeStart = start  # thời gian bắt đầu timestamp
        self.timeEnd = end  # thời gian kết thúc
        self.time = int((end - start) / 3600)  # đổi ra số tiếng kéo dài
        self.name = ""  # tên máy
        self.count = 0  # số máy của loại máy trong hệ thống
        self.productivity = 0  # số thẻ trên 1 giờ
        self.cost = 0  # chi phí số điện trên 1 giờ
        self.count_worker = 0  # số công nhân cần để vận hành
        self.list_cost_time = []  # list chi phí trong 1 giờ vận hàng máy
        self.list_time = []  # list thời gian
        self.data_time = DataFrame(columns=[x * 3600 + self.timeStart for x in range(
            self.time)])  # danh sách thời gian của các máy từ lúc bắt đầu tới hạn theo dạng bảng với 0 là máy rảnh
        # trong thời gian đó, 1 là máy bận
        self.list_free_time = []  # số máy rảnh trong từng giờ trong khoảng thời gian của đơn hàng


# đối tượng lưu trữ thông tin của đơn hàng
class DonHang:
    def __init__(self):
        self.name = ""  # tên đơn hàng
        self.numberCredit = 0  # số thẻ cần sản xuất của đơn hàng
        self.numberMachine = 0  # số loại máy cần để sản xuất
        self.listMachine = []  # danh sách tên các máy theo thứ tự dây chuyền
        self.cost = 0  # chi phí của đơn hàng -> sẽ được tính sau khi đưa vào chương trình
        self.timeD = 0  # thời gian để thực hiện đơn hàng tính theo giờ
        self.time_start = 0  # thời gian bắt đầu đơn hàng tính theo timestamp
        self.time_end = 0  # thời hạn của đơn hàng tính theo timestamp
        self.day = 1


# đọc các file trong PC vào chỉ chấp nhận .txt
def select_file(entry_input):
    file = filedialog.askopenfilename()
    entry_input.configure(state=NORMAL)
    entry_input.delete(0, 100)  # xóa tên file còn lại trong thanh
    entry_input.insert(END, str(file))  # thêm đường dẫn file mới vào thanh chọn
    entry_input.configure(state=DISABLED)  # thiết lập khóa cứng


# đọc dữ liệu từ các đường dẫn thêm vào từ trước
def read_file(file_cost_time, file_data_may, file_don_hang):
    global listECost
    global listWCost
    global listMachineInfo
    listMachineInfo.clear()

    # đọc file costTime
    dataCost = open(file_cost_time)
    s = dataCost.readline()
    tmp = s[:len(s) - 2].split(" ")
    listECost = list(map(int, tmp))
    s = dataCost.readline()
    tmp = s[:len(s) - 2].split(" ")
    listWCost = list(map(int, tmp))
    dataCost.close()

    # doc file don hang
    dataDonHang = open(file_don_hang)
    donHang.name = dataDonHang.readline()
    donHang.name = donHang.name[:len(donHang.name) - 1]
    donHang.numberCredit = int(dataDonHang.readline())
    s = dataDonHang.readline()
    list_s = s[:len(s) - 1].split(" ")
    donHang.numberMachine = int(list_s[0])
    donHang.listMachine = list_s[1:]
    print(donHang.listMachine)
    donHang.time_start = int(math.ceil(datetime.timestamp(datetime.now()) / 3600) * 3600)
    donHang.time_end = int(dataDonHang.readline())
    donHang.timeD = int((donHang.time_end - donHang.time_start) / 3600)
    day = datetime.fromtimestamp(donHang.time_start)
    print(day)
    hours = int(day.strftime('%H'))
    for x in range(donHang.timeD-1):
        hours += 1
        if hours == 24:
            donHang.day += 1
            hours = 0
    dataDonHang.close()

    # đọc data may
    dataMachine = open(file_data_may)
    machine_Number = int(dataMachine.readline())
    for i in range(machine_Number):
        dataMachine.readline()
        machine = Machine(donHang.time_start, donHang.time_end)
        s = str(dataMachine.readline())
        machine.name = s[:len(s) - 1]
        machine.productivity = int(dataMachine.readline())
        machine.cost = float(dataMachine.readline())
        machine.count_worker = int(dataMachine.readline())
        machine.count = int(dataMachine.readline())

        # đọc vào các khoảng thời gian bận của máy
        for j in range(machine.count):
            # danh sách thời gian rảnh/bận của từng máy trong khoảng thời gian đơn hàng
            lTime = [0 for x in range(machine.time)]
            s = str(dataMachine.readline())
            s = s[:len(s) - 1]
            sListTime = s.split(" ")
            iListTime = []  # danh sách thời gian máy j bận trong khoảng thời gian đơn hàng
            for k in range(int(sListTime[0])):  # phần tử đầu tiên của dòng là số thời gian bận của từng máy
                hours = int(sListTime[k + 1])
                if donHang.time_start <= hours < donHang.time_end:
                    lTime[int((hours - donHang.time_start) / 3600)] = 1  # máy j tại thời gian đó bận
                if donHang.time_start <= hours:
                    iListTime.append(hours)
            machine.list_time.append(iListTime)
            l1 = [lTime]
            # tạo bảng thời gian rảnh/ bận của máy thứ j
            df = DataFrame(l1, columns=[(x * 3600 + machine.timeStart) for x in range(machine.time)])
            machine.data_time = machine.data_time.append(df, ignore_index=True)  # thêm vào bảng chính
        for j in range(machine.time):
            # tổng số máy rảnh tại giờ thứ j tính từ thời điểm bắt đầu đơn hàng
            x = machine.data_time[j * 3600 + machine.timeStart].value_counts()
            try:
                machine.list_free_time.append(x[0])
            except:
                machine.list_free_time.append(0)
        day = datetime.fromtimestamp(donHang.time_start)
        dayOfWeek = int(day.strftime('%w'))  # tính ngày trong tuần bắt đầu đơn hàng
        if dayOfWeek == 0:
            dayOfWeek = 7
        hours = int(day.strftime('%H'))  # tính giờ trong ngày bắt đầu đơn hàng
        index = (dayOfWeek - 1) * 24 + hours
        # tính chi phí của từng giờ của máy trong khoảng thời gian đơn hàng
        # hàm chạy theo thứ tự giờ trong tuần khi chạy hết tuần sẽ trở về ngày đầu của tuần
        for j in range(machine.time):
            if index == 24 * 7:
                index = 0
            costT = listECost[index] * machine.cost + listWCost[index] * machine.count_worker
            machine.list_cost_time.append(costT)
            index = index + 1
        listMachineInfo.append(machine)
    dataMachine.close()


#  đọc file đầu vào và giải
def solve():
    global listWork
    listWork.clear()
    file_data_may_name = data_may_input.get()
    file_cost_time_name = cost_time_input.get()
    file_don_hang_name = don_hang_input.get()

    st = datetime.now()

    read_file(file_cost_time_name, file_data_may_name, file_don_hang_name)
    for i in range(donHang.numberMachine):
        for j in range(len(listMachineInfo)):
            if donHang.listMachine[i] == listMachineInfo[j].name:
                listWork.append(listMachineInfo[j])

    numberCredit = donHang.numberCredit
    timeD = donHang.timeD
    numberMachine = donHang.numberMachine
    listProductivity = []
    listCredit = []
    listCost = []
    result = -1
    list_work_result = []
    list_credit_result = []
    if donHang.timeD <= 0:
        return result, list_work_result, list_credit_result

    for i in range(numberMachine):
        listProductivity.append(listWork[i].productivity)
        listCredit.append(listWork[i].list_free_time)
        listCost.append(listWork[i].list_cost_time)

    print(listProductivity)

    solver = pywraplp.Solver.CreateSolver('CBC')

    X = [[solver.IntVar(0, numberCredit, 'x(' + str(i) + ',' + str(j) + ')') for j in range(timeD)] for i in
         range(numberMachine)]
    c = [[solver.IntVar(0, numberCredit, 'c(' + str(i) + ',' + str(j) + ')') for j in range(timeD)] for i in
         range(numberMachine)]
#    num = [[solver.IntVar(0, numberCredit, 'n(' + str(i) + ',' + str(j) + ')') for j in range(timeD)] for i in
#          range(numberMachine)]

    for i in range(numberMachine):
        ctr = solver.Constraint(numberCredit, numberCredit)
        for j in range(timeD):
            ctr.SetCoefficient(X[i][j], 1)

#    for i in range(numberMachine):
#        for j in range(timeD):
#            solver.Add(X[i][j] == num[i][j] * listProductivity[i])

    for i in range(numberMachine):
        for j in range(timeD):
            solver.Add(X[i][j] <= listCredit[i][j]*listProductivity[i])
#            solver.Add(num[i][j] <= listCredit[i][j])

    for i in range(numberMachine):
        for j in range(timeD):
            solver.Add(c[i][j] == sum(X[i][t] for t in range(j + 1)))

    for i in range(1, numberMachine):
        ctr = solver.Constraint(0, 0)
        ctr.SetCoefficient(c[i][0], 1)

    for i in range(1, numberMachine):
        for j in range(1, timeD):
            solver.Add(c[i][j] <= c[i - 1][j - 1])

    obj = solver.Objective()
    for i in range(numberMachine):
        for j in range(timeD):
            obj.SetCoefficient(X[i][j], listCost[i][j]/listProductivity[i])
#            obj.SetCoefficient(num[i][j], listCost[i][j])

    obj.SetMinimization()
    result_status = solver.Solve()
    if result_status == pywraplp.Solver.OPTIMAL:
        result = obj.Value()
        for i in range(numberMachine):
            list_tmp = []
            for j in range(timeD):
                # print(int(X[i][j].solution_value()), end=" ")
                list_tmp.append(int(X[i][j].solution_value()))
            list_credit_result.append(list_tmp)
            # print()
        for i in range(numberMachine):
            list_tmp = []
            for j in range(timeD):
                # print(int(num[i][j].solution_value()), end=" ")
                list_tmp.append(math.ceil(list_credit_result[i][j] / listProductivity[i]))
            list_work_result.append(list_tmp)
            # print()
#        for i in list_credit_result:
#            print(i)
#        for i in list_work_result:
#            print(i)
    else:
        print("Không thể thực hiện được")
    print(datetime.now() - st)
    return result, list_work_result, list_credit_result


# hiện thị kết quả ra màn hình
def show_result():
    global list_credit_result
    global list_num_machine_result
    # chạy chương trình giải ghi kết quả ra file
    donHang.cost, list_num_machine_result, list_credit_result = solve()
    if donHang.cost == -1:
        messagebox.showwarning('Cảnh báo', 'Không có thể hoàn thành đơn hàng')
    else:
        if len(subWin) != 0:  # nếu có nhiều hơn 1 cửa sổ con đang hiển thị thì xóa đi cửa sổ cũ tạo cửa sổ mới
            subWin[0].destroy()
            subWin.clear()
        subWin.append(Toplevel(window))

        # Tạo giao diện cơ bản
        subWin[0].title("Kết quả")
        subWin[0].geometry('500x420')
        subWin[0].resizable(width=0, height=0)
        main_sub = Frame(subWin[0])
        main_sub.pack(fill="both", expand=1)
        canvas_sub = Canvas(main_sub)
        scrollbar_sub = Scrollbar(main_sub, orient=VERTICAL, command=canvas_sub.yview)
        scrollbar_sub.pack(side=RIGHT, fil=Y)
        canvas_sub.configure(yscrollcommand=scrollbar_sub.set)
        canvas_sub.pack(side=LEFT, fill=BOTH, expand=1)
        canvas_sub.bind('<Configure>', lambda e: canvas_sub.configure(scrollregion=canvas_sub.bbox("all")))
        show_result = Frame(canvas_sub)
        canvas_sub.create_window((0, 0), window=show_result, anchor="nw")

        # Hiện thị thông tin đơn hàng
        info = Frame(show_result)
        info.grid(sticky=W)
        Label(info, text="Thông tin đơn hàng").grid()
        Label(info, text="Tên đơn hàng: " + donHang.name).grid(sticky=W)
        Label(info, text="Số Thẻ: " + str(donHang.numberCredit)).grid(sticky=W)
        Label(info, text="số máy thực hiện: " + str(donHang.numberMachine)).grid(sticky=W)
        Label(info, text="Thứ tự các máy: " + str(donHang.listMachine)).grid(sticky=W)
        Label(info, text="Thời gian bắt đầu: " + str(datetime.fromtimestamp(donHang.time_start))).grid(sticky=W)
        Label(info, text="Thời gian kết thúc: " + str(datetime.fromtimestamp(donHang.time_end))).grid(sticky=W)
        Label(info, text="Chi phí: " + str(donHang.cost)).grid(sticky=W)

        # Thiết lập các nút bấm lựa chọn biểu đồ
        cost_list = Frame(show_result)
        cost_list.grid(sticky=W)
        Button(cost_list, text="Biểu đồ tổng quan đơn hàng", command=show_plot).grid(sticky=W)
        Button(cost_list, text="Bảng tổng quan đơn hàng", command=show_table).grid(sticky=W)
        Button(cost_list, text="Bảng rút gọn đơn hàng", command=show_short_table).grid(sticky=W)
        Button(cost_list, text="Chi phí hoạt động", command=show_costList).grid(sticky=W)

        # Thiết lập các nút bấm lựa chọn thông tin các máy
        buttonMachine = Frame(show_result)
        buttonMachine.grid()
        for i in range(len(listMachineInfo)):
            button = Button(buttonMachine, text=listMachineInfo[i].name, command=partial(show_resultButton, i))
            button.grid(row=int(i / 3), column=int(i % 3), padx=10, pady=10)

        writeF = Frame(show_result)
        writeF.grid(sticky=W)
        Button(writeF, text="Ghi kết quả ra file", command=write_to_file).grid(sticky=W)
        for i in range(donHang.numberMachine):
            change_data_frame_machine(i)
#            print(listWork[i].data_time)


def write_to_file():
    fp = open("Data_may.txt", "w")
    n = len(listMachineInfo)
    fp.write(str(n) + "\n")
    for i in range(n):
        fp.write("\n")
        fp.write(str(listMachineInfo[i].name) + "\n")
        fp.write(str(listMachineInfo[i].count) + "\n")
        fp.write(str(listMachineInfo[i].productivity) + "\n")
        fp.write(str(listMachineInfo[i].cost) + "\n")
        fp.write(str(listMachineInfo[i].count_worker) + "\n")
        for j in range(listMachineInfo[i].count):
            s = str(len(listMachineInfo[i].list_time[j])) + " "
            listMachineInfo[i].list_time[j].sort()
            for k in listMachineInfo[i].list_time[j]:
                s += str(k) + " "
            s1 = s[:len(s) - 1]
            s1 += "\n"
            fp.write(s1)
    fp.close()
    messagebox.showinfo("Thông báo", "Đã ghi lại dữ liệu")


# Hiện thị ma trận chi phí hoạt động
def show_costList():
    if len(subWin) == 2:
        subWin[1].destroy()
        subWin.pop(1)
    subWin.append(Toplevel(subWin[0]))

    # Tạo giao diện cơ bản và thanh trượt
    subWin[1].title("Chi phí hoạt động")
    subWin[1].geometry('800x650')
    main_sub = Frame(subWin[1])
    main_sub.pack(fill="both", expand=1)
    canvas_sub = Canvas(main_sub)
    canvas_sub.pack(side=LEFT, fill=BOTH, expand=1)
    scrollbar_sub = Scrollbar(main_sub, orient=VERTICAL, command=canvas_sub.yview)
    scrollbar_sub.pack(side=RIGHT, fil=Y)
    canvas_sub.configure(yscrollcommand=scrollbar_sub.set)
    canvas_sub.bind('<Configure>', lambda e: canvas_sub.configure(scrollregion=canvas_sub.bbox("all")))
    show_result = Frame(canvas_sub)
    canvas_sub.create_window((0, 0), window=show_result, anchor="nw")

    # Tạo ra 2 tap con lựa chọn xem các loại biểu đồ khác nhau
    tap_control = Notebook(show_result)
    tap_costE = Frame(tap_control)
    tap_costW = Frame(tap_control)
    tap_control.add(tap_costE, text='Giá điện')
    tap_control.add(tap_costW, text='Giá công nhân')
    tap_control.pack()

    dateOfWeek = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật']

    # Biểu đồ giá điện tại mỗi ngày trong tuần
    fig, pic = plt.subplots(3, 3, figsize=(10, 8), dpi=80)
    fig.suptitle('Giá điện mỗi giờ')
    for i in range(7):
        tem = []
        for j in range(24):
            tem.append(listECost[i * 24 + j])
        r = int(i / 3)
        c = int(i % 3)
        pic[r][c].plot(tem)
        pic[r][c].set_xlabel('giờ')
        pic[r][c].set_ylabel('số điện')
        pic[r][c].set_yticks((1, 2, 3))
        pic[r][c].set_yticklabels((1, 2, 3))
        pic[r][c].set_xticks((0, 6, 12, 18, 24))
        pic[r][c].set_xticklabels((0, 6, 12, 18, 24))
        pic[r][c].set_title(dateOfWeek[i])

    # Thiết lập 2 khung hình thừa không hiện thị do rạo ra 3x3 khung hình
    pic[2][2].set_visible(False)
    pic[2][1].set_visible(False)

    plt.subplots_adjust(hspace=0.5, wspace=0.5)  # tạo khoảng các giữa các biểu đồ con

    # Thêm vào frame
    line = FigureCanvasTkAgg(fig, tap_costE)
    line.get_tk_widget().pack()

    # Biểu đồ giá công nhân mỗi ngày trong tuần
    fig, pic = plt.subplots(3, 3, figsize=(10, 8), dpi=80)
    fig.suptitle('Giá công nhân')
    for i in range(7):
        tem = []
        for j in range(24):
            tem.append(listWCost[i * 24 + j])
        r = int(i / 3)
        c = int(i % 3)
        pic[r][c].plot(tem)
        pic[r][c].set_xlabel('giờ')
        pic[r][c].set_ylabel('số tiền')
        #        pic[r][c].set_yticks((1, 2, 3))
        #        pic[r][c].set_yticklabels((1, 2, 3))
        pic[r][c].set_xticks((0, 6, 12, 18, 24))
        pic[r][c].set_xticklabels((0, 6, 12, 18, 24))
        pic[r][c].set_title(dateOfWeek[i])

    # Thiết lập 2 khung hình thừa không hiện thị do rạo ra 3x3 khung hình
    pic[2][2].set_visible(False)
    pic[2][1].set_visible(False)

    plt.subplots_adjust(hspace=0.5, wspace=0.5)  # tạo khoảng các giữa các biểu đồ con

    # Thêm vào frame
    line = FigureCanvasTkAgg(fig, tap_costW)
    line.get_tk_widget().pack()


# Hiện thị kết quả dưới dạng biểu đồ
def show_plot():
    global pic, fig, annotate_pic, sc
    while len(subWin) >= 2:
        subWin[1].destroy()
        subWin.pop(1)
    # Tạo giao diện cơ bản
    subWin.append(Toplevel(subWin[0]))
    subWin[1].title("Chi phí hoạt động")
    subWin[1].geometry('1700x900')
    main_sub = Frame(subWin[1])
    main_sub.pack(fill="both", expand=1)
    canvas_sub = Canvas(main_sub)
    scrollbar_sub_y = Scrollbar(main_sub, orient=VERTICAL, command=canvas_sub.yview)
    scrollbar_sub_y.pack(side=RIGHT, fill=Y)
    canvas_sub.configure(yscrollcommand=scrollbar_sub_y.set)
    scrollbar_sub_x = Scrollbar(main_sub, orient=HORIZONTAL, command=canvas_sub.xview)
    scrollbar_sub_x.pack(side=BOTTOM, fill=X)
    canvas_sub.configure(xscrollcommand=scrollbar_sub_x.set)
    canvas_sub.pack(side=LEFT, fill=BOTH, expand=1)
    canvas_sub.bind('<Configure>', lambda e: canvas_sub.configure(scrollregion=canvas_sub.bbox("all")))
    show_result = Frame(canvas_sub)
    canvas_sub.create_window((0, 0), window=show_result, anchor="nw")

    # Đọc file kết quả lấy dữ liệu về lịch làm việc
    # Lịch làm việc của các máy
    print("t", donHang.day)
    str_text.clear()
    x_ax = []
    y_ax = []
    # c = np.random.randint(1, 5, size=15)
    color_point = []
    fig, pic = plt.subplots(1, 1, figsize=(19, 10), dpi=80)
    annotate_pic = pic.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="w"),
                                arrowprops=dict(arrowstyle="wedge"))
    annotate_pic.set_visible(False)
    fig.suptitle('Biểu đồ tổng quan đơn hàng')
    list_curr_credit_plt = [0 for x in range(donHang.numberMachine)]  # danh sách các thẻ của mỗi máy đã được vẽ lên
    # biểu đồ
    x1 = np.arange(0, donHang.timeD, 0.1)
    colors = matplotlib.cm.rainbow(np.linspace(0, 1, donHang.numberMachine))

    for i in range(donHang.numberMachine):
        for j in range(len(list_credit_result[i])):
            if list_credit_result[i][j] != 0:  # nếu máy hoạt động trong khoảng thời gian đó
                yl1 = list_curr_credit_plt[i]  # giới hạn dưới của biểu đồ là số lượng thẻ cũ
                list_curr_credit_plt[i] = list_curr_credit_plt[i] + list_credit_result[i][j]
                yl2 = list_curr_credit_plt[i]  # giới hạn trên của biểu đồ là số lượng thẻ sau
                pic.fill_between(x1, yl1, yl2, where=(x1 >= j) & (x1 <= j + 1), color=colors[i])
                pic.plot([j, j + 1], [yl1, yl1], 'k')
                pic.plot([j, j + 1], [yl2, yl2], 'k')
                pic.plot([j, j], [yl1, yl2], 'k')
                pic.plot([j + 1, j + 1], [yl1, yl2], 'k')
                x_ax.append(j + 0.5)
                y_ax.append(yl2 - 2)
                color_point.append(colors[i])
                text = ""
                text += "Công đoạn số: " + str(i + 1) + "\n"
                text += "Loại máy thực hiện: " + listWork[i].name + "\n"
                text += "chi phí : " + str(list_credit_result[i][j] * listWork[i].list_cost_time[j]) + "\n"
                text += "Thời gian bắt đầu: " + str(datetime.fromtimestamp(donHang.time_start + 3600 * j)) + "\n"
                text += "số máy thực hiện: " + str(int(list_credit_result[i][j] / listWork[i].productivity)) + "\n"
                text += "số thẻ hoàn thành: " + str(int(list_credit_result[i][j])) + "\n"
                str_text.append(text)

    sc = plt.scatter(x_ax, y_ax, c=color_point)
    list_legend = []  # Chú thích
    pic.set_xticks([i * 3 for i in range(0, int(math.ceil(donHang.timeD / 3)))])  # chia trục X thành các khoảng h % 3 = 0
    pic.set_xlim(-1, donHang.timeD)
    pic.set_ylim(-1, donHang.numberCredit + len(listMachineInfo))  # tăng độ cao của trục y để thêm bảng chú thích
    for i in range(donHang.numberMachine):  # vẽ các chấm màu để chú thích cho các cột
        list_legend.append(plt.plot(1, 2, color=colors[i]))
    pic.legend([i[0] for i in list_legend], [i.name for i in listWork], ncol=2, title="Chú thích")  # tạo chú thích
    pic.set_xlabel("Thời gian")
    pic.set_ylabel("Số thẻ")
    x_labels = []
    day = datetime.fromtimestamp(donHang.time_start)
    hours = int(day.strftime('%H'))
    h = 0
    for i in range(donHang.timeD):
        if h == 24:
            h = 0
        if (h + hours) % 3 == hours:
            x_labels.append(h + hours)
        h = h + 1
#    print(x_labels)
    pic.set_xticklabels(x_labels)

    #    plt.subplots_adjust(hspace=0.5, wspace=0.5)
    fig.canvas.mpl_connect("motion_notify_event", hover)
    line = FigureCanvasTkAgg(fig, show_result)
    line.get_tk_widget().pack()


# Hiển thị kết quả dưới dạng bảng
def show_table():
    while len(subWin) >= 2:
        subWin[1].destroy()
        subWin.pop(1)
    # Tạo giao diện cơ bản
    subWin.append(Toplevel(subWin[0]))
    subWin[1].title("Bảng chi tiết hoạt động")
#    subWin[1].geometry('1000x900')
    main_sub = Frame(subWin[1])
    main_sub.pack(fill="both", expand=1)
    canvas_sub = Canvas(main_sub)
    scrollbar_sub_y = Scrollbar(main_sub, orient=VERTICAL, command=canvas_sub.yview)
    scrollbar_sub_y.pack(side=RIGHT, fill=Y)
    canvas_sub.configure(yscrollcommand=scrollbar_sub_y.set)
    scrollbar_sub_x = Scrollbar(main_sub, orient=HORIZONTAL, command=canvas_sub.xview)
    scrollbar_sub_x.pack(side=BOTTOM, fill=X)
    canvas_sub.configure(xscrollcommand=scrollbar_sub_x.set)
    canvas_sub.pack(side=LEFT, fill=BOTH, expand=1)
    canvas_sub.bind('<Configure>', lambda e: canvas_sub.configure(scrollregion=canvas_sub.bbox("all")))
    show_result = Frame(canvas_sub)
    canvas_sub.create_window((0, 0), window=show_result, anchor="nw")

    list_num = []
    for i in range(donHang.numberMachine):
        list_tmp = []
        t = 3600 * int(donHang.time_start / 3600)
        for j in range(donHang.day*24):
            if donHang.time_start <= t < donHang.time_end:
                list_tmp.append(list_num_machine_result[i][int((t - donHang.time_start) / 3600)])
            else:
                list_tmp.append(0)
            t += 3600
        list_num.append(list_tmp)

    time = donHang.time_start
#    Label(show_result, text="Bảng chi tiết hoạt động").pack()
    for i in range(donHang.day):
        labelDay = Frame(show_result)
        labelDay.pack()
        x = datetime.fromtimestamp(time)
        day = x.strftime("%x")
        Label(labelDay, text="Ngày: " + str(day)).grid(sticky=W)
        for j in range(donHang.numberMachine):
            Label(labelDay, text=" Công đoạn: " + str(j+1)).grid(sticky=W)
            Label(labelDay, text="  Tên loại máy: " + donHang.listMachine[j]).grid(sticky=W)
            table = Frame(labelDay)
            table.grid(sticky=W)
            timeEntry = Entry(table, width=10)
            numEntry = Entry(table, width=10)
            timeEntry.grid(row=0, column=0)
            numEntry.grid(row=1, column=0)
            timeEntry.insert(END, "Thời gian")
            numEntry.insert(END, "Số máy")
            timeEntry.configure(state=DISABLED)
            numEntry.configure(state=DISABLED)
            for x in range(24):
                timeEntry = Entry(table, width=8)
                numEntry = Entry(table, width=8)
                timeEntry.grid(row=0, column=x+1)
                numEntry.grid(row=1, column=x+1)
                timeEntry.insert(END, str(x) + "h - " + str(x+1) + "h")
                numEntry.insert(END, str(list_num[j][x+24*i]))
                timeEntry.configure(state=DISABLED)
                numEntry.configure(state=DISABLED)
        time += 3600 * 24
        Label(labelDay, text='\n').grid(sticky=W)


def show_short_table():
    while len(subWin) >= 2:
        subWin[1].destroy()
        subWin.pop(1)
        # Tạo giao diện cơ bản
    subWin.append(Toplevel(subWin[0]))
    subWin[1].title("Bảng chi tiết hoạt động")
    subWin[1].geometry('445x500')
    subWin[1].resizable(width=0, height=100)
    main_sub = Frame(subWin[1])
    main_sub.pack(fill="both", expand=1)
    canvas_sub = Canvas(main_sub)
    scrollbar_sub_y = Scrollbar(main_sub, orient=VERTICAL, command=canvas_sub.yview)
    scrollbar_sub_y.pack(side=RIGHT, fill=Y)
    canvas_sub.configure(yscrollcommand=scrollbar_sub_y.set)
    scrollbar_sub_x = Scrollbar(main_sub, orient=HORIZONTAL, command=canvas_sub.xview)
    scrollbar_sub_x.pack(side=BOTTOM, fill=X)
    canvas_sub.configure(xscrollcommand=scrollbar_sub_x.set)
    canvas_sub.pack(side=LEFT, fill=BOTH, expand=1)
    canvas_sub.bind('<Configure>', lambda e: canvas_sub.configure(scrollregion=canvas_sub.bbox("all")))
    show_result = Frame(canvas_sub)
    canvas_sub.create_window((0, 0), window=show_result, anchor="nw")

    table = Frame(show_result)
    table.grid(row=0, column=0)
    a = Entry(table, width=10)
    a.grid(row=0, column=0)
    a.insert(END, "Ngày")
    a.configure(state=DISABLED)
    a = Entry(table, width=10)
    a.grid(row=0, column=1)
    a.insert(END, "Giờ")
    a.configure(state=DISABLED)
    a = Entry(table, width=15)
    a.grid(row=0, column=2)
    a.insert(END, "Tên máy")
    a.configure(state=DISABLED)
    a = Entry(table, width=10)
    a.grid(row=0, column=3)
    a.insert(END, "Số máy")
    a.configure(state=DISABLED)
    a = Entry(table, width=10)
    a.grid(row=0, column=4)
    a.insert(END, "Số thẻ")
    a.configure(state=DISABLED)
    a = Entry(table, width=10)
    a.grid(row=0, column=5)
    a.insert(END, "Công đoạn")
    a.configure(state=DISABLED)
    r = 0
    last = 0
    i_last = 0
    for i in range(donHang.timeD):
        for j in range(donHang.numberMachine):
            if list_num_machine_result[j][i] != 0:
                r += 1
                t = datetime.fromtimestamp(donHang.time_start + 3600*i)
                a = Entry(table, width=10)
                a.grid(row=r, column=0)
                if math.floor((donHang.time_start + 3600*i) / 86400) != last:
                    a.insert(END, str(t.strftime("%x")))
                    last = math.floor((donHang.time_start + 3600*i) / 86400)
                a.configure(state=DISABLED)
                a = Entry(table, width=10)
                a.grid(row=r, column=1)
                if i_last != i:
                    a.insert(END,  str(t.strftime("%X")))
                    i_last = i
                a.configure(state=DISABLED)
                a = Entry(table, width=15)
                a.grid(row=r, column=2)
                a.insert(END, donHang.listMachine[j])
                a.configure(state=DISABLED)
                a = Entry(table, width=10)
                a.grid(row=r, column=3)
                a.insert(END, list_num_machine_result[j][i])
                a.configure(state=DISABLED)
                a = Entry(table, width=10)
                a.grid(row=r, column=4)
                a.insert(END, list_credit_result[j][i])
                a.configure(state=DISABLED)
                a = Entry(table, width=10)
                a.grid(row=r, column=5)
                a.insert(END, str(j+1))
                a.configure(state=DISABLED)


def update_annotate(ind):
    pos = sc.get_offsets()[ind["ind"][0]]
    annotate_pic.xy = pos
    text = str_text[ind['ind'][0]]
    annotate_pic.set_text(text)
    # set mau


def hover(event):
    vis = annotate_pic.get_visible()
    if event.inaxes == pic:
        cont, ind = sc.contains(event)
        if cont:
            update_annotate(ind)
            annotate_pic.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                annotate_pic.set_visible(False)
                fig.canvas.draw_idle()


# Hiện thị thông tin sau của các máy
def show_resultButton(i):
    if len(subWin) >= 2:
        for j in range(1, len(subWin)):
            subWin[1].destroy()
            subWin.pop(1)
    subWin.append(Toplevel(subWin[0]))
    subWin[1].title(listMachineInfo[i].name)
    subWin[1].resizable(width=0, height=0)
    main_sub = Frame(subWin[1])
    main_sub.pack(fill="both", expand=1)
    canvas_sub = Canvas(main_sub)
    canvas_sub.pack(side=LEFT, fill=BOTH, expand=1)
    scrollbar_sub = Scrollbar(main_sub, orient=VERTICAL, command=canvas_sub.yview)
    scrollbar_sub.pack(side=RIGHT, fil=Y)
    canvas_sub.configure(yscrollcommand=scrollbar_sub.set)
    canvas_sub.bind('<Configure>', lambda e: canvas_sub.configure(scrollregion=canvas_sub.bbox("all")))
    show_result = Frame(canvas_sub)
    canvas_sub.create_window((0, 0), window=show_result, anchor="nw")

    machineInfoFrame = Frame(show_result)
    machineInfoFrame.grid(sticky=W)
    Label(machineInfoFrame, text="Tên loại máy: " + listMachineInfo[i].name).grid(sticky=W)
    Label(machineInfoFrame, text="Số máy trong hệ thống: " + str(listMachineInfo[i].count)).grid(sticky=W)
    Label(machineInfoFrame, text="Năng suất của máy: " + str(listMachineInfo[i].productivity) + " thẻ / giờ").grid(
        sticky=W)
    Label(machineInfoFrame, text="Số điện mỗi giờ: " + str(listMachineInfo[i].cost)).grid(sticky=W)
    Label(machineInfoFrame, text="Số công nhân để hoạt động: " + str(listMachineInfo[i].count_worker)).grid(sticky=W)

    listCostFrame = Frame(show_result)
    listCostFrame.grid()
    Button(listCostFrame, text="Biểu đồ", command=partial(show_button_plot, i)).grid(row=0, column=0)
    machineEntry = Entry(listCostFrame, width=10)
    listEntry = Entry(listCostFrame, width=20)
    nameEntry = Entry(listCostFrame, width=15)
    machineEntry.grid(row=1, column=0)
    listEntry.grid(row=1, column=1)
    nameEntry.grid(row=1, column=2)
    machineEntry.insert(END, "Máy số")
    listEntry.insert(END, "Thời gian")
    nameEntry.insert(END, "Tên hợp đồng")
    machineEntry.configure(state=DISABLED)
    listEntry.configure(state=DISABLED)
    nameEntry.configure(state=DISABLED)
    for x in range(int(listMachineInfo[i].count)):
        machineEntry = Entry(listCostFrame, width=10)
        listEntry = Entry(listCostFrame, width=20)
        nameEntry = Entry(listCostFrame, width=15)
        machineEntry.grid(row=x + 2, column=0)
        listEntry.grid(row=x + 2, column=1)
        nameEntry.grid(row=x + 2, column=2)
        machineEntry.insert(END, (x + 1))
        machineEntry.configure(state=DISABLED)
        listEntry.configure(state=DISABLED)
        nameEntry.configure(state=DISABLED)


def change_data_frame_machine(ind):
    column = listWork[ind].data_time.columns
    index = listWork[ind].data_time.index
    x = 0
    for i in column:
        num = list_num_machine_result[ind][x]
        if num != 0:
            for j in index:
                if listWork[ind].data_time[i].loc[j] == 0:
                    listWork[ind].data_time[i].loc[j] = -1
                    listWork[ind].list_time[j].append(i)
                    num -= 1
                    if num == 0:
                        break
        x += 1


def show_button_plot(index):
    global pic, fig, annotate_pic, sc
    while len(subWin) >= 3:
        subWin[2].destroy()
        subWin.pop(2)
    # Tạo giao diện cơ bản
    subWin.append(Toplevel(subWin[1]))
    subWin[2].title("Chi phí hoạt động")
    subWin[2].geometry('1000x700')
    main_sub = Frame(subWin[2])
    main_sub.pack(fill="both", expand=1)
    canvas_sub = Canvas(main_sub)
    canvas_sub.pack(side=LEFT, fill=BOTH, expand=1)
    scrollbar_sub = Scrollbar(main_sub, orient=VERTICAL, command=canvas_sub.yview)
    scrollbar_sub.pack(side=RIGHT, fil=Y)
    canvas_sub.configure(yscrollcommand=scrollbar_sub.set)
    canvas_sub.bind('<Configure>', lambda e: canvas_sub.configure(scrollregion=canvas_sub.bbox("all")))
    show_result = Frame(canvas_sub)
    canvas_sub.create_window((0, 0), window=show_result, anchor="nw")

    # Đọc file kết quả lấy dữ liệu về lịch làm việc

    str_text.clear()
    x_ax = []
    y_ax = []
    # c = np.random.randint(1, 5, size=15)
    color_point = []
    fig, pic = plt.subplots(1, 1, figsize=(12, 8), dpi=80)
    annotate_pic = pic.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="w"),
                                arrowprops=dict(arrowstyle="wedge"))
    annotate_pic.set_visible(False)
    fig.suptitle('Biểu đồ thời gian từng máy')

    # biểu đồ
    x1 = np.arange(0, donHang.timeD, 0.1)
    colors = matplotlib.cm.rainbow(np.linspace(0, 1, 2))

    x = 0
    y = 0
    for i in listMachineInfo[index].data_time.columns:
        for j in listMachineInfo[index].data_time.index:
            if listMachineInfo[index].data_time[i].loc[j] == -1:
                yl1 = i
                yl1 -= donHang.time_start
                yl1 /= 3600
                pic.fill_between(x1, j, j + 1, where=(x1 >= yl1) & (x1 <= yl1 + 1), color=colors[0])
                pic.plot([yl1, yl1], [j, j + 1], 'k')
                pic.plot([yl1 + 1, yl1 + 1], [j, j + 1], 'k')
                pic.plot([yl1, yl1 + 1], [j, j], 'k')
                pic.plot([yl1, yl1 + 1], [j + 1, j + 1], 'k')
            if listMachineInfo[index].data_time[i].loc[j] == 1:
                yl1 = i
                yl1 -= donHang.time_start
                yl1 /= 3600
                pic.fill_between(x1, j, j + 1, where=(x1 >= yl1) & (x1 <= yl1 + 1), color=colors[1])
                pic.plot([yl1, yl1], [j, j + 1], 'k')
                pic.plot([yl1 + 1, yl1 + 1], [j, j + 1], 'k')
                pic.plot([yl1, yl1 + 1], [j, j], 'k')
                pic.plot([yl1, yl1 + 1], [j + 1, j + 1], 'k')
    '''
    index_result = -1
    for i in range(len(listWork)):
        if listWork[i].name == listMachineInfo[index].name:
            index_result = i
            break
    if index_result != -1:
        curr_credit_plt = 0  # danh sách các thẻ của mỗi máy đã được vẽ lên
        for i in range(len(list_result_work[index_result])):
            if list_result_work[index_result][i] != 0:  # nếu máy hoạt động trong khoảng thời gian đó
                if list_result_work[index_result][i] != -1:  # nếu máy hoàn thành việc sản xuất thẻ hoàn chỉnh
                    yl1 = curr_credit_plt  # giới hạn dưới của biểu đồ là số lượng thẻ cũ
                    curr_credit_plt = curr_credit_plt + list_result_work[index_result][i]
                    yl2 = curr_credit_plt  # giới hạn trên của biểu đồ là số lượng thẻ sau
                    number_machine = list_result_work[index_result][i]
                    time = donHang.time_start + i * 3600
                    for j in range(len(listMachineInfo[index].list_time)):
                        iContinue = 0
                        for k in listMachineInfo[index].list_time[j]:
                            if k == time:
                                iContinue = 1
                                break
                        if iContinue == 0:
                            pic.fill_between(x1, j, j + 1, where=(x1 >= i + 1) & (x1 <= i + 1), color=colors[1])
                            pic.plot([i + 1, i + 1], [j, j], 'k')
                            pic.plot([i + 1, i + 1], [j + 1, j + 1], 'k')
                            pic.plot([i + 1, i + 1], [j, j + 1], 'k')
                            pic.plot([i + 1, i + 1], [j, j + 1], 'k')
                            x_ax.append(i + 0.5)
                            y_ax.append(j + 0.5)
                            color_point.append(colors[1])
                            text = ""
                            text += "Tên hợp đồng: " + donHang.name + "\n"
                            text += "Máy số " + str(j + 1) + "\n"
                            text += "Công đoạn số " + str(index_result + 1) + "\n"
                            text += "Sử dụng từ: " + str(datetime.fromtimestamp(time - 3600 * (ic - 1))) + "\n"
                            text += "Thời gian sử dụng: " + str(ic) + " giờ\n"
                            text += "Thực hiện thẻ số " + str(yl1) + " đến thẻ số " + str(yl2) + "\n"
                            str_text.append(text)
                            number_machine -= math.ceil(listMachineInfo[index].productivity)
                            if number_machine == 0:
                                break

    '''
    sc = plt.scatter(x_ax, y_ax, c=color_point)
    list_legend = []  # Chú thích
    pic.set_xticks([i * 3 for i in range(0, int(math.ceil(donHang.timeD / 3)))])  # chia trục X thành các khoảng h % 3 = 0
    pic.set_xlim(-1, donHang.timeD)
    pic.set_ylim(-1, listMachineInfo[index].count + 5)  # tăng độ cao của trục y để thêm bảng chú thích
    for i in range(2):  # vẽ các chấm màu để chú thích cho các cột
        list_legend.append(plt.plot(1, 2, color=colors[i]))
    pic.legend([i[0] for i in list_legend], ["của hợp đồng hiện tại", "của các hợp đồng trước"], ncol=1,
               title="Chú thích thời gian bận")  # tạo chú thích
    pic.set_xlabel("Thời gian")
    pic.set_ylabel("Máy")
    x_labels = []
    day = datetime.fromtimestamp(donHang.time_start)
    hours = int(day.strftime('%H'))
    for i in range(donHang.timeD):
        if hours == 24:
            hours = 0
        if hours % 3 == 0:
            x_labels.append(hours)
        hours = hours + 1
    pic.set_xticklabels(x_labels)

    #    plt.subplots_adjust(hspace=0.5, wspace=0.5)
    fig.canvas.mpl_connect("motion_notify_event", hover)
    line = FigureCanvasTkAgg(fig, show_result)
    line.get_tk_widget().pack()


def reset_data():
    confirm = messagebox.askquestion("Xác nhận", "Xóa hết dữ liệu cũ?")
    if confirm == 'yes':
        fp = open("Data_may.txt")
        list_machine = []
        n = int(fp.readline())
        for i in range(n):
            fp.readline()
            machine = Machine(0, 0)
            s = fp.readline()
            machine.name = s[:len(s)-1]
            machine.count = int(fp.readline())
            machine.productivity = int(fp.readline())
            machine.cost = int(fp.readline())
            machine.count_worker = int(fp.readline())
            for j in range(machine.count):
                fp.readline()
            list_machine.append(machine)
        fp.close()

        fp = open("Data_may.txt", "w")
        fp.write(str(n) + "\n")
        for i in range(n):
            fp.write("\n")
            fp.write(str(list_machine[i].name) + "\n")
            fp.write(str(list_machine[i].count) + "\n")
            fp.write(str(list_machine[i].productivity) + "\n")
            fp.write(str(list_machine[i].cost) + "\n")
            fp.write(str(list_machine[i].count_worker) + "\n")
            for j in range(list_machine[i].count):
                fp.write("0\n")
        fp.close()
        messagebox.showinfo("Thông báo", "Đã cài lại dữ liệu")


# main
fig, pic = plt.subplots(1, 1, figsize=(19, 10), dpi=80)
annotate_pic = pic.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="wedge"))
str_text = []
sc = plt.scatter([1], [1])

# danh sách biến
root = Tk()  # cửa sổ chính
subWin = []  # list các cửa sổ con
listMachineInfo = []  # thông tin máy trong file data_may
listECost = []  # thông tin giá điện theo giờ 24/7
listWCost = []  # thông tin giá công nhân theo giờ 24/7
donHang = DonHang()  # thông tin đơn hàng
listWork = []  # danh sách các máy sẽ thực hiện đơn hàng
list_credit_result = []
list_num_machine_result = []

file_data_may_name = ""
file_cost_time_name = ""
file_don_hang_name = ""

# create window scroll
main_frame = Frame(root)
main_frame.pack(fill="both", expand=1)
canvas = Canvas(main_frame)
canvas.pack(side=LEFT, fill=BOTH, expand=1)
scrollbar_x = Scrollbar(main_frame, orient=VERTICAL, command=canvas.xview)
scrollbar_x.pack(side=BOTTOM, fil=X)
scrollbar_y = Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
scrollbar_y.pack(side=RIGHT, fil=Y)
canvas.configure(xscrollcommand=scrollbar_x.set)
canvas.configure(yscrollcommand=scrollbar_y.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
window = Frame(canvas)
canvas.create_window((0, 0), window=window, anchor="nw")

root.title("Test app")
root.geometry('600x400')
root.resizable(width=0, height=0)
title = Frame(window)
title.grid(sticky=W)
file_data_may = Label(title, text="Data máy")

file_data_may.grid(row=0, column=0)
data_may_input = Entry(title, width=50)
data_may_input.grid(row=0, column=1, padx=5)
data_may_input.insert(END, "Data_may.txt")
data_may_input.configure(state=DISABLED)
Button(title, text="Chọn file", command=partial(select_file, data_may_input)).grid(row=0, column=2, padx=5)

file_cost_time = Label(title, text="Cost time")
file_cost_time.grid(row=1, column=0)
cost_time_input = Entry(title, width=50)
cost_time_input.grid(row=1, column=1, padx=5)
cost_time_input.insert(END, "costTime.txt")
cost_time_input.configure(state=DISABLED)
Button(title, text="Chọn file", command=partial(select_file, cost_time_input)).grid(row=1, column=2, padx=5)

file_don_hang = Label(title, text="Đơn hàng")
file_don_hang.grid(row=2, column=0)
don_hang_input = Entry(title, width=50)
don_hang_input.grid(row=2, column=1, padx=5)
don_hang_input.insert(END, "Data_donhang.txt")
don_hang_input.configure(state=DISABLED)
Button(title, text="Chọn file", command=partial(select_file, don_hang_input)).grid(row=2, column=2, padx=5)

window_machine = Frame(window)
window_machine.grid()

button_show_result = Button(window, text="Xác nhận", command=show_result)
button_show_result.grid(sticky=W, pady=10)

button_delete_data = Button(window, text="Xóa dữ liệu", command=reset_data)
button_delete_data.grid(sticky=W, pady=10)


def closing():
    root.destroy()
    sys.exit()


root.protocol("WM_DELETE_WINDOW", closing)
window.mainloop()

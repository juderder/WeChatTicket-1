from codex.baseview import APIView
from codex.baseerror import ValidateError, PrivilegeError, DatabaseError, LogicError
from wechat.views import CustomWeChatView
from WeChatTicket import settings
from wechat.models import Activity, Ticket
from adminpage.models import Image
from django.db.models import Q
import time


class ActivityList(APIView):

    def activity_to_dict(self, activity):
        activity_dict = {}
        activity_dict['id'] = activity.id
        activity_dict['name'] = activity.name
        activity_dict['description'] = activity.description
        activity_dict['startTime'] = time.mktime(activity.start_time.timetuple())
        activity_dict['endTime'] = time.mktime(activity.end_time.timetuple())
        activity_dict['place'] = activity.place
        activity_dict['bookStart'] = time.mktime(activity.book_start.timetuple())
        activity_dict['bookEnd'] = time.mktime(activity.book_end.timetuple())
        activity_dict['currentTime'] = int(time.time())
        activity_dict['status'] = activity.status
        return activity_dict

    def get(self):
        activity_set = Activity.objects.exclude(status=-1)
        activity_list = []
        for item in activity_set:
            item_dict = self.activity_to_dict(item)
            activity_list.append(item_dict)
        return activity_list


class ActivityDelete(APIView):

    def post(self):
        self.check_input('id')
        try:
            activity = Activity.objects.get(id=self.input['id'])
        except Activity.DoesNotExist:
            raise DatabaseError(self.input)
        if activity.status == Activity.STATUS_DELETED:
            raise LogicError(self.input)
        activity.status = Activity.STATUS_DELETED
        activity.save()


# 时间存在问题
class ActivityCreate(APIView):

    def post(self):
        self.check_input('name', 'key', 'place', 'picUrl', 'startTime', 'endTime', 'bookStart', 'bookEnd', 'totalTickets', 'status')
        Activity.objects.create(name=self.input['name'], key=self.input['key'], place=self.input['place'],
                                description=self.input['description'], start_time=self.input['startTime'], pic_url=self.input['picUrl'],
                                end_time=self.input['endTime'], book_start=self.input['bookStart'], book_end=self.input['bookEnd'],
                                total_tickets=self.input['totalTickets'], status=self.input['status'], remain_tickets=self.input['totalTickets'])


class ImageLoader(APIView):

    def post(self):
        self.check_input('image')
        i = Image(image=self.request.FILES['image'])
        i.save()
        image_url = settings.SITE_DOMAIN + "/wechat/media/upload_img/" + str(self.input['image'][0])
        return image_url


class ActivityDetail(APIView):

    def get_used_ticket_num(self, activity):
        ticket_set = Ticket.objects.filter(Q(activity=activity, status=Ticket.STATUS_USED))
        return len(ticket_set)

    def activity_to_dict(self, activity):
        activity_dict = {}
        activity_dict['name'] = activity.name
        activity_dict['key'] = activity.key
        activity_dict['description'] = activity.description
        activity_dict['startTime'] = time.mktime(activity.start_time.timetuple())
        activity_dict['endTime'] = time.mktime(activity.end_time.timetuple())
        activity_dict['place'] = activity.place
        activity_dict['bookStart'] = time.mktime(activity.book_start.timetuple())
        activity_dict['bookEnd'] = time.mktime(activity.book_end.timetuple())
        activity_dict['totalTickets'] = activity.total_tickets
        activity_dict['picUrl'] = activity.pic_url
        activity_dict['bookedTickets'] = activity.total_tickets - activity.remain_tickets
        activity_dict['usedTickets'] = self.get_used_ticket_num(activity)
        activity_dict['currentTime'] = int(time.time())
        activity_dict['status'] = activity.status
        return activity_dict

    def change_activity_detail(self, activity):
        # 所有情况下都可以修改
        activity.description = self.input['description']
        activity.pic_url = self.input['picUrl']
        # 已发布活动不可修改
        activity.name = self.input['name']
        activity.place = self.input['place']
        activity.status = self.input['status']

        # 抢票开始后不可修改
        activity.total_tickets = self.input['totalTickets']

        # 活动结束后不可修改
        activity.start_time = self.input['startTime']
        activity.end_time = self.input['endTime']
        # 已发布活动不可修改
        activity.book_start = self.input['bookStart']
        # 活动开始后不可修改
        activity.book_end = self.input['bookEnd']
        activity.save()

    def get(self):
        self.check_input('id')
        try:
            choosen_activity = Activity.objects.get(id=self.input['id'])
        except:
            raise DatabaseError(self.input)
        choosen_activity_dict = self.activity_to_dict(choosen_activity)
        return choosen_activity_dict

    def post(self):
        self.check_input('id', 'name', 'place', 'picUrl', 'startTime', 'endTime', 'bookStart', 'bookEnd', 'totalTickets', 'status')
        try:
            choosen_activity = Activity.objects.get(id=self.input['id'])
        except:
            raise DataBaseError(self.input)
        self.change_activity_detail(choosen_activity)


class ActivityMenu(APIView):

    def get(self):
        pass

    def post(self):
        pass


class ActivityCheckin(APIView):

    def checkin_ticket(self):
        ticket = Ticket.objects.get(unique_id=self.input['ticket'])
        activity = Activity.objects.get(id=self.input['actId'])
        if ticket.activity == activity and ticket.status == Ticket.STATUS_VALID:
            ticket_info_dict = {}
            ticket_info_dict['ticket'] = self.input['ticket']
            ticket_info_dict['studentId'] = ticket.student_id
            return ticket_info_dict
        else:
            raise ValidateError(self.input)

    def checkin_student_id(self):
        ticket_list = Ticket.objects.filter(student_id=self.input['studentId'])
        activity = Activity.objects.get(id=self.input['actId'])
        for ticket in ticket_list:
            if ticket.activity == activity and ticket.status == Ticket.STATUS_VALID:
                ticket_info_dict = {}
                ticket_info_dict['ticket'] = ticket.unique_id
                ticket_info_dict['studentId'] = ticket.student_id
                return ticket_info_dict
        raise ValidateError(self.input)

    def post(self):
        self.check_input('actId')
        if 'ticket' in self.input.keys():
            return self.checkin_ticket()
        elif 'studentId' in self.input.keys():
            return self.checkin_student_id()

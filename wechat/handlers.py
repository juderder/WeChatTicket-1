# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler


__author__ = "Epsirom"


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
            self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        self.user.student_id = ''
        self.user.save()
        return self.reply_text(self.get_message('unbind_account'))


class BindAccountHandler(WeChatHandler):

    def check(self):
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind'])

    def handle(self):
        return self.reply_text(self.get_message('bind_account'))


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))


# 抢啥：显示三天内可抢票活动
class ActivityQueryHandler(WeChatHandler):

    def check(self):
        return self.is_text('近期活动') or self.is_text("我好无聊") or self.is_event_click(self.view.event_keys['book_what'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))


# 查票：查看用户自己获得的票
class TicketQueryHandler(WeChatHandler):

    def check(self):
        return self.is_text('查票') or self.is_event_click(self.view.event_keys['get_ticket'])

    def handle(self):
        pass

class InvalidMathExpressionHandler(WeChatHandler):

    def check(self):
        return self.is_math_expression() and not self.is_valid_math_expression()

    def handle(self):
        return self.reply_text(self.get_message('invalid_math_expression'))


class ValidMathExpressionHandler(WeChatHandler):

    def check(self):
        return self.is_math_expression() and self.is_valid_math_expression()

    def handle(self):
        math_result = self.get_math_expression_value()
        return self.reply_text(self.get_message('math_result', math_result=math_result))

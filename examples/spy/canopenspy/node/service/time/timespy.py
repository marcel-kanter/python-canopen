from canopen.node.service.time import TIMEConsumer


class TIMESpy(TIMEConsumer):
	def on_time(self, message):
		print(message)
		TIMEConsumer.on_time(self, message)

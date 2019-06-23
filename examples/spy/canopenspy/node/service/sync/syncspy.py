from canopen.node.service.sync import SYNCConsumer


class SYNCSpy(SYNCConsumer):
	def on_sync(self, message):
		print(message)
		SYNCConsumer.on_sync(self, message)

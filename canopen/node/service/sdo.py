from .service import Service


class SDOServer(Service):
	def __init__(self):
		Service.__init__(self)
	
	def attach(self, node):
		Service.attach(self, node)
		self._node.network.subscribe(self.on_request, 0x600 + self._node.id)
	
	def detach(self):
		if self._node == None:
			raise RuntimeError()
		
		self._node.network.unsubscribe(self.on_request, 0x600 + self._node.id)
		Service.detach(self)
	
	def on_request(self, message):
		if message.dlc != 8:
			return
		
		command = message.data[0] & 0xE0
		if command == 0x00: # Download segment
			self._on_download_segment(message)
		if command == 0x20: # Initiate download
			self._on_initiate_download(message)
		if command == 0x40: # Initiate upload
			self._on_initiate_upload(message)
		if command == 0x60: # Upload segment
			self._on_upload_segment(message)
		if command == 0x80: # Abort transfer
			self._on_abort(message)
		if command == 0xA0: # Block upload
			self._on_block_upload(message)
		if command == 0xC0: # Block download
			self._on_block_download(message)
		if command == 0xE0: # Network indication
			self._on_network_indication(message)
	
	def _on_download_segment(self, message):
		pass
	
	def _on_initiate_download(self, message):
		pass
	
	def _on_initiate_upload(self, message):
		pass
	
	def _on_upload_segment(self, message):
		pass
	
	def _on_abort(self, message):
		pass
	
	def _on_block_upload(self, message):
		pass
	
	def _on_block_download(self, message):
		pass
	
	def _on_network_indication(self, message):
		pass

class InputHandler:
    def __init__(self):
        self.keys = {}
        self.mouse_buttons = {}
    
    def update(self):
        self.keys = {key: False for key in range(256)}  # Reset keys
        self.mouse_buttons = {button: False for button in range(3)}  # Reset mouse buttons

    def get_key(self, key):
        return self.keys.get(key, False)

    def get_mouse_button(self, button):
        return self.mouse_buttons.get(button, False)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.keys[event.key] = True
        elif event.type == pygame.KEYUP:
            self.keys[event.key] = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_buttons[event.button] = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_buttons[event.button] = False
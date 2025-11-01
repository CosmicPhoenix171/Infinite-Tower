import pygame


class InputHandler:
    """
    Centralized input handling system for keyboard and mouse events.
    
    This class manages input state and provides a clean interface for
    checking key and mouse button states throughout the game.
    """
    
    def __init__(self):
        self.keys = {}  # For event-based key tracking
        self.mouse_buttons = {}
        self.mouse_pos = (0, 0)
        self._pressed_keys_array = None

    def update(self):
        """Update input states. Call this once per frame."""
        # Get current pygame key states as an array
        self._pressed_keys_array = pygame.key.get_pressed()
        
        # Get current mouse button states
        mouse_buttons = pygame.mouse.get_pressed()
        self.mouse_buttons = {i: mouse_buttons[i] for i in range(len(mouse_buttons))}
        
        # Update mouse position
        self.mouse_pos = pygame.mouse.get_pos()

    def get_key(self, key):
        """Check if a specific key is currently pressed."""
        # Use the pressed keys array if available
        if self._pressed_keys_array is not None:
            try:
                # pygame.key.get_pressed() returns True/False for each key
                # Key constants like pygame.K_w should work directly if < 512
                if key < 512:
                    return self._pressed_keys_array[key]
            except (IndexError, TypeError):
                pass
        
        # Fallback: check event-based key tracking
        return self.keys.get(key, False)

    def get_mouse_button(self, button):
        """Check if a specific mouse button is currently pressed."""
        return self.mouse_buttons.get(button, False)
    
    def get_mouse_pos(self):
        """Get the current mouse position as (x, y) tuple."""
        return self.mouse_pos

    def handle_event(self, event):
        """
        Handle individual pygame events for state changes.
        Call this for each event in the event loop.
        """
        if event.type == pygame.KEYDOWN:
            self.keys[event.key] = True
        elif event.type == pygame.KEYUP:
            self.keys[event.key] = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_buttons[event.button] = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_buttons[event.button] = False
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
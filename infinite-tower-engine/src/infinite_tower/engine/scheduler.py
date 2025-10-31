"""
Infinite Tower Engine - Task Scheduler Module

Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.
"""

from typing import Callable, List, Optional, Any
import time


class ScheduledTask:
    """
    Represents a scheduled task with timing information.
    """
    
    def __init__(self, callback: Callable, delay: float, repeat: bool = False, 
                 repeat_interval: float = 0, task_id: Optional[str] = None):
        self.callback = callback
        self.delay = delay  # Time until next execution (in seconds or frames)
        self.initial_delay = delay
        self.repeat = repeat
        self.repeat_interval = repeat_interval
        self.task_id = task_id
        self.active = True
        self.execution_count = 0
    
    def execute(self) -> bool:
        """
        Execute the task callback.
        
        Returns:
            True if task should continue (for repeating tasks)
        """
        if not self.active:
            return False
        
        self.callback()
        self.execution_count += 1
        
        if self.repeat:
            self.delay = self.repeat_interval
            return True
        
        return False
    
    def cancel(self):
        """Cancel this task."""
        self.active = False


class Scheduler:
    """
    Task scheduler for managing timed events and recurring tasks.
    
    Features:
    - One-time delayed tasks
    - Repeating tasks
    - Frame-based or time-based timing
    - Task cancellation and management
    """
    
    def __init__(self, use_real_time: bool = False):
        """
        Initialize scheduler.
        
        Args:
            use_real_time: If True, use real time (seconds). If False, use frame count.
        """
        self.timed_tasks: List[ScheduledTask] = []
        self.use_real_time = use_real_time
        self.total_time = 0.0
        self.frame_count = 0
        self.task_id_counter = 0
    
    def add_task(self, callback: Callable, delay: float, 
                 task_id: Optional[str] = None) -> ScheduledTask:
        """
        Schedule a one-time task.
        
        Args:
            callback: Function to call
            delay: Delay before execution (seconds or frames)
            task_id: Optional identifier for the task
            
        Returns:
            ScheduledTask instance
        """
        if task_id is None:
            task_id = f"task_{self.task_id_counter}"
            self.task_id_counter += 1
        
        task = ScheduledTask(callback, delay, repeat=False, task_id=task_id)
        self.timed_tasks.append(task)
        return task
    
    def add_repeating_task(self, callback: Callable, interval: float,
                          initial_delay: Optional[float] = None,
                          task_id: Optional[str] = None) -> ScheduledTask:
        """
        Schedule a repeating task.
        
        Args:
            callback: Function to call
            interval: Time between executions
            initial_delay: Initial delay before first execution (defaults to interval)
            task_id: Optional identifier for the task
            
        Returns:
            ScheduledTask instance
        """
        if task_id is None:
            task_id = f"repeat_task_{self.task_id_counter}"
            self.task_id_counter += 1
        
        delay = initial_delay if initial_delay is not None else interval
        task = ScheduledTask(callback, delay, repeat=True, 
                           repeat_interval=interval, task_id=task_id)
        self.timed_tasks.append(task)
        return task
    
    def add_event(self, event: Callable, delay: float):
        """
        Legacy method for backward compatibility.
        
        Args:
            event: Function to call
            delay: Delay before execution
        """
        self.add_task(event, delay)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task by ID.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if task was found and cancelled
        """
        for task in self.timed_tasks:
            if task.task_id == task_id:
                task.cancel()
                return True
        return False
    
    def cancel_all_tasks(self):
        """Cancel all scheduled tasks."""
        for task in self.timed_tasks:
            task.cancel()
    
    def update(self, delta_time: float):
        """
        Update all scheduled tasks.
        
        Args:
            delta_time: Time elapsed since last update (seconds or 1 for frame-based)
        """
        if self.use_real_time:
            self.total_time += delta_time
        else:
            self.frame_count += 1
        
        # Update and execute tasks
        tasks_to_remove = []
        
        for task in self.timed_tasks:
            if not task.active:
                tasks_to_remove.append(task)
                continue
            
            task.delay -= delta_time
            
            if task.delay <= 0:
                # Execute task
                should_continue = task.execute()
                
                if not should_continue:
                    tasks_to_remove.append(task)
        
        # Remove completed tasks
        for task in tasks_to_remove:
            if task in self.timed_tasks:
                self.timed_tasks.remove(task)
    
    def get_active_task_count(self) -> int:
        """Get number of active tasks."""
        return len([t for t in self.timed_tasks if t.active])
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """
        Get a task by ID.
        
        Args:
            task_id: Task identifier
            
        Returns:
            ScheduledTask or None
        """
        for task in self.timed_tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def clear(self):
        """Remove all tasks."""
        self.timed_tasks.clear()


class Timer:
    """
    Simple timer for measuring elapsed time.
    """
    
    def __init__(self):
        self.start_time = 0.0
        self.elapsed_time = 0.0
        self.is_running = False
    
    def start(self):
        """Start the timer."""
        self.start_time = time.time()
        self.is_running = True
    
    def stop(self) -> float:
        """
        Stop the timer and return elapsed time.
        
        Returns:
            Elapsed time in seconds
        """
        if self.is_running:
            self.elapsed_time = time.time() - self.start_time
            self.is_running = False
        return self.elapsed_time
    
    def reset(self):
        """Reset the timer."""
        self.start_time = 0.0
        self.elapsed_time = 0.0
        self.is_running = False
    
    def get_elapsed(self) -> float:
        """
        Get elapsed time without stopping.
        
        Returns:
            Elapsed time in seconds
        """
        if self.is_running:
            return time.time() - self.start_time
        return self.elapsed_time


class FrameRateManager:
    """
    Manages frame rate and provides delta time calculations.
    """
    
    def __init__(self, target_fps: int = 60):
        self.target_fps = target_fps
        self.target_frame_time = 1.0 / target_fps
        self.last_frame_time = time.time()
        self.delta_time = 0.0
        self.fps = 0.0
        self.frame_times = []
        self.max_samples = 60
    
    def tick(self) -> float:
        """
        Calculate delta time and update FPS.
        
        Returns:
            Delta time in seconds
        """
        current_time = time.time()
        self.delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Update FPS calculation
        self.frame_times.append(self.delta_time)
        if len(self.frame_times) > self.max_samples:
            self.frame_times.pop(0)
        
        if self.frame_times:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            self.fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        return self.delta_time
    
    def get_fps(self) -> float:
        """Get current FPS."""
        return self.fps
    
    def get_delta_time(self) -> float:
        """Get last frame's delta time."""
        return self.delta_time
    
    def limit_frame_rate(self, clock: Any):
        """
        Limit frame rate using pygame clock.
        
        Args:
            clock: pygame.time.Clock instance
        """
        clock.tick(self.target_fps)
import json
import time
import math
import pygame

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 120, 255)
RED = (255, 0, 0)
GREY = (150, 150, 150)
DARK_GREY = (50, 50, 50)
FPS = 60

# --- Load Animation Plan ---
def load_plan(path: str = "timeline.json"):
    """Loads the animation plan from the JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["animation_plan"]
    except FileNotFoundError:
        print(f"Error: Could not find '{path}'. Please generate it first by running the 'timeline' command.")
        return None

# --- Drawing Functions ---
def draw_detailed_robot(surface, head_tilt, left_arm_angle, right_arm_angle, mouth_state="neutral", eye_state="open"):
    """Draws a more detailed robot on the screen based on current angles and states."""
    
    # Body Parameters
    body_width = 80
    body_height = 160
    shoulder_offset_x = body_width // 2 + 10 # Arms start slightly outside body
    arm_length = 90
    forearm_length = 60
    head_radius = 45
    
    # Robot origin points
    body_center_x, body_bottom_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100
    body_top_y = body_bottom_y - body_height
    neck_base_x, neck_base_y = body_center_x, body_top_y

    # --- Torso ---
    pygame.draw.rect(surface, BLUE, (body_center_x - body_width // 2, body_top_y, body_width, body_height))
    
    # --- Head ---
    head_center_x = neck_base_x + head_radius * math.sin(math.radians(head_tilt))
    head_center_y = neck_base_y - head_radius - (head_radius * math.cos(math.radians(head_tilt)))
    pygame.draw.circle(surface, GREY, (int(head_center_x), int(head_center_y)), head_radius)
    
    # Neck Joint (connect head to body)
    pygame.draw.line(surface, DARK_GREY, (neck_base_x, neck_base_y), (int(head_center_x), int(head_center_y - head_radius)), 8)

    # Eyes
    eye_offset_x = 15
    eye_offset_y = 10
    left_eye_center = (int(head_center_x - eye_offset_x), int(head_center_y - eye_offset_y))
    right_eye_center = (int(head_center_x + eye_offset_x), int(head_center_y - eye_offset_y))
    
    if eye_state == "closed":
        pygame.draw.line(surface, BLACK, (left_eye_center[0] - 8, left_eye_center[1]), (left_eye_center[0] + 8, left_eye_center[1]), 3)
        pygame.draw.line(surface, BLACK, (right_eye_center[0] - 8, right_eye_center[1]), (right_eye_center[0] + 8, right_eye_center[1]), 3)
    else: # Open eyes
        pygame.draw.circle(surface, BLACK, left_eye_center, 8)
        pygame.draw.circle(surface, BLACK, right_eye_center, 8)
        pygame.draw.circle(surface, WHITE, (left_eye_center[0] + 3, left_eye_center[1] - 3), 3) # Eye glint
        pygame.draw.circle(surface, WHITE, (right_eye_center[0] + 3, right_eye_center[1] - 3), 3) # Eye glint

    # Mouth
    mouth_y_offset = 20
    mouth_x1 = int(head_center_x - 15)
    mouth_x2 = int(head_center_x + 15)
    mouth_y = int(head_center_y + mouth_y_offset)

    if mouth_state == "smile":
        pygame.draw.arc(surface, BLACK, (mouth_x1, mouth_y - 5, mouth_x2 - mouth_x1, 20), math.pi, 2*math.pi, 3)
    elif mouth_state == "sad":
        pygame.draw.arc(surface, BLACK, (mouth_x1, mouth_y + 5, mouth_x2 - mouth_x1, 20), 0, math.pi, 3)
    else: # Neutral/straight line
        pygame.draw.line(surface, BLACK, (mouth_x1, mouth_y), (mouth_x2, mouth_y), 3)


    # --- Arms ---
    # Left Arm (Robot's left, your right)
    shoulder_l_x, shoulder_l_y = neck_base_x - shoulder_offset_x, neck_base_y + 20
    elbow_l_x = shoulder_l_x + arm_length * math.cos(math.radians(left_arm_angle))
    elbow_l_y = shoulder_l_y - arm_length * math.sin(math.radians(left_arm_angle))
    wrist_l_x = elbow_l_x + forearm_length * math.cos(math.radians(left_arm_angle - 90)) # Forearm bent
    wrist_l_y = elbow_l_y - forearm_length * math.sin(math.radians(left_arm_angle - 90))
    
    pygame.draw.line(surface, DARK_GREY, (shoulder_l_x, shoulder_l_y), (elbow_l_x, elbow_l_y), 15)
    pygame.draw.line(surface, DARK_GREY, (elbow_l_x, elbow_l_y), (wrist_l_x, wrist_l_y), 10)
    pygame.draw.circle(surface, RED, (int(wrist_l_x), int(wrist_l_y)), 10) # Hand

    # Right Arm (Robot's right, your left)
    shoulder_r_x, shoulder_r_y = neck_base_x + shoulder_offset_x, neck_base_y + 20
    elbow_r_x = shoulder_r_x - arm_length * math.cos(math.radians(right_arm_angle))
    elbow_r_y = shoulder_r_y - arm_length * math.sin(math.radians(right_arm_angle))
    wrist_r_x = elbow_r_x - forearm_length * math.cos(math.radians(right_arm_angle - 90)) # Forearm bent
    wrist_r_y = elbow_r_y - forearm_length * math.sin(math.radians(right_arm_angle - 90))
    
    pygame.draw.line(surface, DARK_GREY, (shoulder_r_x, shoulder_r_y), (elbow_r_x, elbow_r_y), 15)
    pygame.draw.line(surface, DARK_GREY, (elbow_r_x, elbow_r_y), (wrist_r_x, wrist_r_y), 10)
    pygame.draw.circle(surface, RED, (int(wrist_r_x), int(wrist_r_y)), 10) # Hand


# --- Main Animation Loop ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Expressive Gesture Robot")
    clock = pygame.time.Clock()

    plan = load_plan()
    if not plan:
        return

    # Robot's initial state
    head_tilt = 0
    left_arm_angle = 60  # Arms slightly down
    right_arm_angle = 60
    mouth_state = "neutral"
    eye_state = "open"

    running = True
    plan_index = 0
    start_time = time.time()
    
    # Store dynamic gesture parameters to smooth transitions
    current_gesture_start_time = 0
    current_gesture_duration = 0
    current_gesture_name = "neutral"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_elapsed_time = time.time() - start_time
        
        # Check if we need to update the current gesture based on the plan
        if plan_index < len(plan) and current_elapsed_time >= plan[plan_index]["start"]:
            current_gesture_name = plan[plan_index]["gesture"]
            current_gesture_start_time = plan[plan_index]["start"]
            current_gesture_duration = plan[plan_index]["end"] - plan[plan_index]["start"]
            print(f"Time: {current_elapsed_time:.2f}s, Gesture: {current_gesture_name}")
            plan_index += 1

        # Calculate time within the current gesture for animation phasing
        gesture_progress = 0
        if current_gesture_duration > 0:
             gesture_progress = (current_elapsed_time - current_gesture_start_time) / current_gesture_duration
             gesture_progress = max(0, min(1, gesture_progress)) # Clamp between 0 and 1

        # --- GESTURE TO MOVEMENT MAPPING ---
        # Reset to defaults for neutral or unrecognized gestures
        head_tilt = 0
        left_arm_angle = 60  # Default pose
        right_arm_angle = 60
        mouth_state = "neutral"
        eye_state = "open"

        if current_gesture_name == "wave":
            right_arm_angle = 120 + 30 * math.sin(current_elapsed_time * 5) # Oscillate right arm for wave
        elif current_gesture_name == "nod":
            head_tilt = 15 * math.sin(current_elapsed_time * 8) # Nod head up/down
        elif current_gesture_name == "shake_head":
            head_tilt = 25 * math.sin(current_elapsed_time * 8) # Shake head left/right
        elif current_gesture_name == "thumbs_up":
            right_arm_angle = 130 # Arm up for thumbs up
            left_arm_angle = 60
        elif current_gesture_name == "celebrate":
            left_arm_angle = 120 + 20 * math.sin(current_elapsed_time * 10)
            right_arm_angle = 120 + 20 * math.cos(current_elapsed_time * 10) # Both arms wave excitedly
            mouth_state = "smile"
        elif current_gesture_name == "think":
            head_tilt = -15 # Slight head tilt
            right_arm_angle = 90 # Hand near chin
            mouth_state = "neutral"
        elif current_gesture_name == "shrug":
            left_arm_angle = 100 # Shoulders up
            right_arm_angle = 100
            head_tilt = 0 # Head neutral
            mouth_state = "sad"
        elif current_gesture_name == "point_right":
            right_arm_angle = 120 # Pointing arm out
            left_arm_angle = 60
            head_tilt = 20 # Look in direction of pointing
        elif current_gesture_name == "point_left":
            left_arm_angle = 120 # Pointing arm out
            right_arm_angle = 60
            head_tilt = -20 # Look in direction of pointing
        elif current_gesture_name == "explain_open_hands":
            left_arm_angle = 90 # Both arms slightly raised, open
            right_arm_angle = 90
        elif current_gesture_name == "face_palm":
            right_arm_angle = 160 # Arm up towards head
            mouth_state = "sad"
            eye_state = "closed"
        elif current_gesture_name == "counting_fingers":
            # Simple alternating arm raise for counting effect
            if (current_elapsed_time % 1.0) < 0.5:
                right_arm_angle = 100
                left_arm_angle = 60
            else:
                right_arm_angle = 60
                left_arm_angle = 100
        elif current_gesture_name == "listening_tilt":
            head_tilt = 15 * math.sin(current_elapsed_time * 3 + math.pi/2) # Slow head tilt to one side
        elif current_gesture_name == "calm_down":
            left_arm_angle = 80 # Arms lower, spread
            right_arm_angle = 80
            mouth_state = "neutral"
            head_tilt = 0

        # --- Drawing ---
        screen.fill(WHITE)
        draw_detailed_robot(screen, head_tilt, left_arm_angle, right_arm_angle, mouth_state, eye_state)
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
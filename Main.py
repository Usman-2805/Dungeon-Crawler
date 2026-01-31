#Algorithms
#Trigonometry - Calculating Bullet Trajectory
#Graph and BFS - Enemy Pathfinding towards the player
#Queue - Used in BFS and used in random enemy generation
#Random Level Generation - Creates a random level every time the player starts a new game
#Advanced Matrix Operation(Dot Product) - Changes the probability of getting something based on what the player chose before
#SQL - Creates a table and inserts data for saving the game and selects the data from the table to load the game
#SQL Aggregate Function - Calculates the average score for each difficulty 
#Merge Sort - Sorts items in the inventory based on type first and then based on the stat of the item
#Stack - Used to changed state of the game between different menus, etc

# Pygame is used to render the game and handle inputs and collisions
import pygame
from pygame.locals import *
# Used for calculating bullet trajectory and square root function when calculating distances
import math
# Used for random number generation, random weighted selection when randomly generating enemies and normal random selection (e.g. Upgrade Screen)
import random
# Used to detect if a file exists (e.g. Save files) and to get file names from the folder items
import os
# Used to create/insert data into a table and is used when saving and loading my game
import sqlite3

pygame.init()
clock = clock = pygame.time.Clock()
flags = RESIZABLE | DOUBLEBUF
screen = pygame.display.set_mode((1920,1200),flags,16)

class Entity:
    def __init__(self,maxhp,name,defence,speed,pos):
        self.Health = maxhp #Current health of the entity
        self.MaxHealth = maxhp #Maximum Health of the entity
        self.Name = name #Name of the entity
        self.Position = pos #Position as a tuple (x,y)
        self.Defence = defence #Defensive stat that reduced incoming damage
        self.Speed = speed #Movement speed of the entity
        
    def GetHealth(self):
        #Returns current health of the entity
        return self.Health
    
    def GetName(self):
        #Returns the name of the entity
        return self.Name
    
    def GetPosition(self):
        #Returns the position of the entity
        return self.Position
    
    def GetSpeed(self):
        #Returns the movement speed of the entity
        return self.Speed
    
    def TakeDamage(self,incoming_damage):
        # Calculates and applies damage reduction based on the entity's defence
        # incoming_damage (int): The raw damage received before mitigation.
        # The final damage taken after applying defence reduction
        if self.Defence > 0:
            # Damage reduction based on defence
            reduction = self.Defence / (self.Defence + 100)
            final_damage = round(incoming_damage *(1-reduction))
            #Ensures damage is not negative
            return max(final_damage, 0)
        else:
            #If defence is 0 then damage is not reduced
            return incoming_damage
    
    def Move(self):
        pass
    
    def Die(self):
        # Checks if the entity has died
        # Returns a true or false depending if they have or haven't
        if self.Health <= 0:
            return True
        else:
            return False

class Bullet:
    def __init__(self,start_x,start_y,final_x,final_y,image,damage):
        #Load and Scale the bullet image
        self.Bullet = pygame.image.load(image).convert_alpha()
        self.Bullet = pygame.transform.scale2x(self.Bullet)
        self.Bullet_Rect = self.Bullet.get_rect(midtop = (start_x,start_y))
        self.player_x = start_x # Initial x-coordinate of the bullet
        self.player_y = start_y # Initial y-coordinate of the bullet
        self.mouse_x = final_x #Target x-coordinate
        self.mouse_y = final_y #Target y-coordinate
        self.hs,self.vs = self.bullet_trajectory() #Trajectory based on starting and target positions
        self.damage = damage #Damage dealt on impact
        self.step = 2 #Speed multiplier
    
    def bullet_trajectory(self):
        #Calculates the difference in the x and y positions
        difference_x = self.mouse_x - self.player_x
        difference_y = self.mouse_y - self.player_y
        # Calcualtes the angle of movement using arctangent function
        # dx is opposite and dy is adjacent of a triangle 
        angle = math.atan2(difference_y,difference_x)
        v = 5 # Base Bullet speed
        
        horizontal_speed = v * math.cos(angle) #Calculates Horizontal Speed
        vertical_speed = v * math.sin(angle) #Calculates Vertical Speed
        return horizontal_speed, vertical_speed
    
    def update_bullet_position(self):
        self.Bullet_Rect.x = self.Bullet_Rect.x + self.hs * self.step #Moves the bullet horizontally
        self.Bullet_Rect.y = self.Bullet_Rect.y + self.vs * self.step #Moves the bullet vertically
    
    def move_bullet(self):
        #Moves the bullet by updating its positon
        self.update_bullet_position()
        
    def check_collision_walls(self,tile_rects):
        #Checks if the bullet collides with any walls
        for tile in tile_rects:
            #Checks if a bullet intersects with a wall
            if tile.colliderect(self.Bullet_Rect):
                return True
    
    def check_collision_entity(self,rect):
        # Checks if it intersects with an entity
        if rect.colliderect(self.Bullet_Rect):
            return True

class Graph:
    def __init__(self,level):
        self.adjacency_matrix_array = [[] * 1 for i in range(120)]
        self.adjacency_matrix = {} # Dictionary to story adjacency list representation
        self.level = level # Room grid structure
        self.nodes = self.get_graph_list() # Extract Valid Nodes from the level
    
    def get_graph_list(self):
        # Makes the grid into node positions
        counter = 0 # Counter for number of walkable nodes
        list_location= [] # Stores valid node positions
        for row_no in range(0,7): # Loop through rows
            for tile_no in range(0,15): # Loop through columns
                tile = self.level[row_no][tile_no] #Get the tile value
                if tile != 0 or tile != 3:
                    list_location.append((tile_no, row_no)) # Add tile position as a node
                    counter += 1 # Increment node count
        return list_location # Return the list of valid nodes
    
    def validate_neighbours(self,neighbours):
        #Makes sures the nods are within range of the walkable area
        new_neighbours = [] # Stores valid neighbors
        for node in neighbours:
            i = node[0] # Extract x-coordinate
            j = node[1] # Extract y-coordinates
            if i < 15 and j < 7 and i > 0 and j > 0:
                new_neighbours.append(node) # Add valid neighbor
        return new_neighbours # Return filtererd neighbors
    
    def make_matrix(self):
        # Gets the neighbours of each node to create a matrix
        counter = 0 # Index Counter
        for node in self.nodes: # Iterate through each valid node
            i = node[0] # x-coordinates
            j = node[1] # y-coordinates
            #  Define possible movement direction (right, left, down, up)
            neighbours = [(i+1,j),(i-1,j),(i,j+1),(i,j-1)]
            # Remove out of bounds neighbors
            neighbours = self.validate_neighbours(neighbours)
            # Store neighbors in the adjacency matrix array
            self.adjacency_matrix_array[counter] = neighbours
            # Insert the current node at the start of the list
            self.adjacency_matrix_array[counter].insert(0,node)
            counter += 1 # Move to the next index
            
    def array_to_dictionary(self):
        # Converts the array to a dictionary
        for i in self.adjacency_matrix_array:
            counter = 0
            neighbours = [] # Store neighbor nodes
            for neighbour in i:
                if counter != 0:
                    neighbours.append(neighbour) # These elements are neighbours
                if counter == 0:
                    node = neighbour # First element is the node itself
                counter += 1 # Increment Counter
            # Only add nodes with neighbors to the adjacency matrix
            if len(neighbours) >0:
                self.adjacency_matrix[node] = neighbours # Stores in dictionary
                
class Enemy(Entity):
    def __init__(self,maxhp, name, strength, defence, speed, acd, pos):
        super().__init__(maxhp, name,defence, speed, pos)
        self.set_avatar()
        self.Strength = strength # Attack power of the enemy
        self.attack_cool_down = acd # Cooldown time between attacks
        self.last_attack = random.randint(3000,10000) # Random initial attack delay
        # Burning status: [isBurning, start_time, last_tick_time]
        self.burning = [False, 0, 0]
        self.burning_damage = 5
        
        # Wind effect: [isAffected, knockback_x, knockback_y]
        self.wind = [False, 0, 0]
        
        self.state = "active"
        self.path = []  # Stores pathfinding route
        self.current_target_move = 1  # Tracks movement progress along path
        self.reached = False  # Whether the enemy has reached its destination
        self.prev = (0, 0)  # Previous position for movement tracking
        
        self.projectiles = [] #Stores all the bullet objects that the enemy shoots
        
        # Movement direction states
        self.move_direction = {'up': False,'down': False,'left': False,'right': False}
        
        self.start = False  # Whether the enemy has started moving
        self.last_start = 0  # Last recorded start time
        self.divide = random.randint(1, 20)  # Random divisor for behavior variation
        
        #Health Bar for enemy
        self.health_bar = HealthBar(50,5,self.MaxHealth)

    def TakeDamage(self,incoming_damage,armor_penetration):
        if self.Defence > 0:
            self.Defence -= self.Defence * armor_penetration # Reduce defence by armor penetration percentage
            reduction = self.Defence / (self.Defence + 100) # Damage reduction formula
            final_damage = round(incoming_damage *(1-reduction))
            return max(final_damage, 0) # Ensure damage isn't negative
        else:
            return incoming_damage # If no defense, take full damage
    def apply_burning_effect(self):
        # Applies burning damage every second if the enemy is burning.
        if self.burning[0]:
            current_time = pygame.time.get_ticks()
            if (current_time - self.burning[2]) >= 1000:
                self.Health -= self.burning_damage
                self.burning[2] = current_time # Reset tick timer
    
    def move_wind(self):
        # Moves the enemy based on wind knockback and gradually reduces knockback force.
        if self.wind[0]:
            if abs(self.wind[1]) > 0.1 or abs(self.wind[2]) > 0.1:
                new_x = self.EnemyRect.x + self.wind[1]
                new_y = self.EnemyRect.y + self.wind[2]
                # Ensure movement is within allowed bounds
                if new_x > 140 and new_x < 1740:
                    self.EnemyRect.x += self.wind[1]
                if new_y > 135 and new_y < 750:
                    self.EnemyRect.y += self.wind[2]
                
                # Gradually reduce knockback effect
                self.wind[1] *= 0.9
                self.wind[2] *= 0.9
            else:
                self.wind[0] = False # Stop wind effect when force is minimal
    
    def check_still_burning(self):
        # Stops burning effect after a set duration (5 seconds).
        duration = 5000
        current_time = pygame.time.get_ticks()
        if (current_time - self.burning[1]) >= duration:
            self.burning[0] = False
        
    def can_start(self):
        #Once enough time has passed the enemies can start to move and attack
        current_time = pygame.time.get_ticks()
        time_difference = current_time - self.last_start
        if  time_difference >= 1500 and self.start == False:
            self.start = True
            self.last_start = current_time
    
    def reset_start(self):
        #Restarts the enemy by making it no longer move and attack
        self.start = False
        self.last_attack = pygame.time.get_ticks()
        self.last_start = pygame.time.get_ticks()
        self.projectiles = []
    
    def set_avatar(self):
        # Assigns an enemy sprite based on its name
        if self.Name == "Skeleton Boss":
            self.Avatar = pygame.image.load('Graphics/Enemies/Bosses/Skeleton Boss.png').convert_alpha()
        if self.Name == "Ghost":
            self.Avatar = pygame.image.load('Graphics/Enemies/Ghost.png').convert_alpha()
        if self.Name == "Ghost Boss":
            self.Avatar = pygame.image.load('Graphics/Enemies/Bosses/Ghost Boss.png').convert_alpha()
        if self.Name == "Skeleton":
            self.Avatar = pygame.image.load('Graphics/Enemies/Skeleton.png').convert_alpha()
        self.EnemyRect = self.Avatar.get_rect(topleft= (self.Position))

    def drop_randomly(self,items,rarities):
        # Selects an item drop based on rarity probabilities
        selected_rarity = self.get_rarity_drop(rarities)
        
        rarity_correct = False
        while not(rarity_correct):
            selected_item= self.select_item(items)
            if not(selected_item is None):
                if selected_item.rarity == selected_rarity:
                    rarity_correct = True
                    return selected_item
    
    def get_rarity_drop(self,rarities):
        # Determines item rarity based on probability distribution
        r = random.random() # Generates a number between 0 and 1
        cumulative = 0
        for rarity in rarities:
            probability = rarities[rarity]
            cumulative += probability
            if r<= cumulative:
                return rarity
        
    def select_item(self,items):
        #Randomly selects and item using a random_number generator
        random_number = random.randint(1,(len(items)-1))
        counter = 1
        for item in items:
            if item != "background":
                if counter == random_number:
                    return Item(item)
            counter += 1
    def can_attack(self):
        # Determines whether the enemy can attack based on cooldown timer.
        current_time = pygame.time.get_ticks()
        if self.start:
            if (current_time - self.last_attack) >= self.attack_cool_down * 1000:
                self.last_attack = current_time
                return True
            else:
                return False

    def Move(self,current_level,Player_pos,tile_rects,door_rects):
        # Updates enemy movement using pathfinding towards the player
        path = self.find_path(current_level,Player_pos)
        if self.path != path:
            self.path = path
            self.prev = path[0]
            self.current_target_move = 1
        if self.start:
            self.Move_along_path(tile_rects,door_rects)
        
    def collision_test(self,tile_rects):
        #Gets all the tiles the enemy is colliding with
        collisioned_tiles = []
        for tile in tile_rects:
            if tile.colliderect(self.EnemyRect):
                collisioned_tiles.append(tile)
        return collisioned_tiles
    
    def keep_within_area_y(self,tile_rects,door_rects):
        #Keeps enemy within the vertical area
        collided_tiles = self.collision_test(tile_rects)
        for tile in collided_tiles:
            #If enemy is moving up and collides, enemy will be moved to the bottom of the colliding tile
            if self.move_direction['up']:
                self.EnemyRect.top = tile.bottom
            #If enemy is moving down and collides, enemy will be moved to the top of the colliding tile
            if self.move_direction['down']:
                self.EnemyRect.bottom = tile.top
        collided_doors = self.collision_test(door_rects)
        for door in collided_doors:
            #If enemy is moving up and collides, enemy will be moved to the bottom of the colliding tile
            if self.move_direction['up']:
                self.EnemyRect.top = door.bottom
            #If enemy is moving down and collides, enemy will be moved to the top of the colliding tile
            if self.move_direction['down']:
                self.EnemyRect.bottom = door.top
    
    def keep_within_area_x(self,tile_rects,door_rects):
        #Keeps enemy within the horizontal area
        collided_tiles = self.collision_test(tile_rects)
        for tile in collided_tiles:
            # If the enemy is moving right and collides it will be moved to the left of the colliding tile
            if self.move_direction['right']:
                self.EnemyRect.right = tile.left
            # If the enemy is moving left and collides it will be moved to the right of the colliding tile
            if self.move_direction['left']:
                self.EnemyRect.left = tile.right
        collided_doors = self.collision_test(door_rects)
        for door in collided_doors:
            # If the enemy is moving right and collides it will be moved to the left of the colliding tile
            if self.move_direction['right']:
                self.EnemyRect.right = door.left
            # If the enemy is moving left and collides it will be moved to the right of the colliding tile
            if self.move_direction['left']:
                self.EnemyRect.left = door.right
    
    def Move_along_path(self,tile_rects,door_rects):
        if self.path and self.current_target_move < len(self.path):
            target_x,target_y = self.path[self.current_target_move]
            movement = [0,0]
            # Determine vertical movement (up or down) if x-coordinate remains the same
            if (target_x - self.prev[0]) == 0:
                #Just want to change the up and down
                dy = self.prev[1] - target_y
                if dy == 1:
                    self.move_direction['up'] = True
                if dy == -1:
                    self.move_direction['down'] = True
            # Determine horizontal movement (left or right) if y-coordinate remains the same
            if (target_y - self.prev[1]) == 0:
                dx = self.prev[0] - target_x
                if dx == 1:
                    self.move_direction['left'] = True
                if dx == -1:
                    self.move_direction['right'] = True
            
            # Move left if possible and not reached destination
            if self.move_direction['left'] == True and self.reached == False:
                self.EnemyRect.x -= 2
                movement[0] += 32
            # Move right if possible and not reached destination
            if self.move_direction['right'] == True and self.reached == False:
                self.EnemyRect.x += 2
                movement[0] += 32
            # Check for collisions in the x-direction and adjust position if necessary
            collided_tiles = self.collision_test(tile_rects)
            self.keep_within_area_x(collided_tiles,door_rects)
            # Move up if possible and not reached destination
            if self.move_direction['up'] == True and self.reached == False:
                self.EnemyRect.y -= 2
                movement[1] += 32
            # Move down if possible and not reached destination
            if self.move_direction['down'] == True and self.reached == False:
                self.EnemyRect.y += 2
                movement[1] += 32
            # Check for collisions in the y-direction and adjust position if necessary
            collided_tiles = self.collision_test(tile_rects)
            self.keep_within_area_y(collided_tiles,door_rects)
            # If the enemy has moved at least 64 steps in either direction, reset movement flags
            if movement[0] >= 64 or movement[1] >= 64:
                self.move_direction['up'] = False
                self.move_direction['down'] = False
                self.move_direction['left'] = False
                self.move_direction['right'] = False
                movement = [0,0] # Reset movement tracker
                    
    def find_path(self,current_level,Player_pos):
        # Uses pathfinding algorithm to find the shortest route to the player
        graph = Graph(current_level)
        graph.make_matrix()
        graph.array_to_dictionary()
        self.adjacency_matrix = graph.adjacency_matrix
        finding = Pathfinding(self.adjacency_matrix)
        # Convert enemy position to grid index
        enemy_pos = (self.EnemyRect.x,self.EnemyRect.y)
        start = finding.find_index(enemy_pos,128,135)
        end = finding.find_index(Player_pos, 128,135)
        return finding.bfs_pathfinding(self.adjacency_matrix,start,end)
    
    def render(self):
        # Draws the enemy on the screen
        screen.blit(self.Avatar,self.EnemyRect)

class Spider(Enemy):
    def __init__(self,maxhp, name, strength, defence, speed,acd, pos):
        # Initialize the Spider class, which inherits from Enemy
        # Projectiles trap the player for half a second(base time) and only moves when the player is trapped
        super().__init__(maxhp, name, strength, defence, speed,acd,pos)
        # List to store projectiles (web shots) fired by the spider
        self.projectiles = []
        self.set_avatar()
        
    def set_avatar(self):
        # Set the spider's avatar based on its name (Boss or regular spider)
        if self.Name == "Spider Boss":
            self.Avatar = pygame.image.load('Graphics/Enemies/Bosses/Spider Boss.png').convert_alpha()
        else:
            self.Avatar = pygame.image.load('Graphics/Enemies/Spider.png').convert_alpha()
        self.EnemyRect = self.Avatar.get_rect(topleft= (self.Position))
            
    
    def create_projectile(self,Playerx,Playery):
        # Create a projectile to fire at the player
        image = 'Graphics/Bullet/BulletC5.png'
        web_proj = Bullet(self.EnemyRect.x,self.EnemyRect.y,Playerx,Playery,image,self.Strength)
        # Adds the projectile to list
        self.projectiles.append(web_proj)
    
    def Attack(self,Player_pos):
        # Creates a projectile to shoot at the player
        self.create_projectile(Player_pos[0],Player_pos[1])
            
    def check_collision_bullet_player(self,Player_rect):
        # Check if any projectiles have collided with the player
        total_damage = 0
        # Iterates through all projectiles and checks for collisions
        for proj in self.projectiles:
            delete = proj.check_collision_entity(Player_rect)
            # Removes the projectile if it collides withthe player and applies damage to the player
            if delete:
                self.projectiles.remove(proj)
                total_damage += proj.damage
        return total_damage
    #This before checking collision with player
    def check_collision_wall(self,current_level_tiles):
        # Check if any projectiles fired hit a wall
        for proj in self.projectiles:
            delete = proj.check_collision_walls(current_level_tiles)
            # Removes the projectile if it collides with a wall
            if delete:
                self.projectiles.remove(proj)

class Fire_Monster(Enemy):
    def __init__(self, maxhp, name, strength, defence, speed,acd, pos):
        # Initialize the Fire Monster class, which inherits from Enemy
        super().__init__( maxhp, name, strength, defence, speed,acd,pos)
        # List to store projectiles (web shots) fired by the spider
        self.projectiles = []
        self.set_avatar()
    
    def set_avatar(self):
        # Set the Fire Monster avatar based on its name (Boss or regular)
        if self.Name == "Fire Boss":
            self.Avatar = pygame.image.load('Graphics/Enemies/Bosses/Fire Boss.png').convert_alpha()
        else:
            self.Avatar = pygame.image.load('Graphics/Enemies/Fire.png').convert_alpha()
        self.EnemyRect = self.Avatar.get_rect(topleft= (self.Position))
    
    def Move(self,current_level,Player_pos,tile_rects,door_rects):
        # The enemy doesn't move at all and is stationary the whole time
        pass
    
    def Attack(self,Player_pos):
        # Creates a projectile to shoot at the player
        self.create_projectile(Player_pos[0],Player_pos[1])
    
    def create_projectile(self,Playerx,Playery):
        # Create a projectile to fire at the player
        image = 'Graphics/Bullet/BulletC4.png'
        fire_proj = Bullet(self.EnemyRect.x,self.EnemyRect.y,Playerx,Playery,image,self.Strength)
        # Adds the projectile to list
        self.projectiles.append(fire_proj)
    
    def check_collision_bullet_player(self,Player_rect):
        # Check if any projectiles have collided with the player
        total_damage = 0
        # Iterates through all projectiles and checks for collisions
        for proj in self.projectiles:
            delete = proj.check_collision_entity(Player_rect)
            # Removes the projectile if it collides withthe player and applies damage to the player
            if delete:
                self.projectiles.remove(proj)
                total_damage += proj.damage
        return total_damage
    #This before checking collision with player
    def check_collision_wall(self,current_level_tiles):
        # Check if any projectiles fired hit a wall
        for proj in self.projectiles:
            delete = proj.check_collision_walls(current_level_tiles)
            # Removes the projectile if it collides with a wall
            if delete:
                self.projectiles.remove(proj)

class Water_Monster(Enemy):
    def __init__(self,  maxhp, name, strength, defence, speed,acd,pos):
        # Initialize the Water Monster class, which inherits from Enemy
        super().__init__( maxhp, name, strength, defence, speed,acd,pos)
        # List to store projectiles (web shots) fired by the spider
        self.projectiles = []
        self.set_avatar()
          
    def set_avatar(self):
        # Set the Water Monster avatar based on its name (Boss or regular)
        if self.Name == "Water Boss":
            self.Avatar = pygame.image.load('Graphics/Enemies/Bosses/Water Boss.png').convert_alpha()
        else:
            self.Avatar = pygame.image.load('Graphics/Enemies/Water.png').convert_alpha()
        self.EnemyRect = self.Avatar.get_rect(topleft= (self.Position))
    
    def Move(self,current_level,Player_pos,tile_rects,door_rects):
        # The enemy doesn't move at all and is stationary the whole time
        pass
    
    def Attack(self,Player_pos):
        # Creates a projectile to shoot at the player
        self.create_projectile(Player_pos[0],Player_pos[1])
    
    def create_projectile(self,Playerx,Playery):
        # Create a projectile to fire at the player
        image = 'Graphics/Bullet/BulletB2.png'
        web_proj = Bullet(self.EnemyRect.x,self.EnemyRect.y,Playerx,Playery,image,self.Strength)
        # Adds the projectile to list
        self.projectiles.append(web_proj)
    
    def check_collision_bullet_player(self,Player_rect):
        # Check if any projectiles have collided with the player
        total_damage = 0
        # Iterates through all projectiles and checks for collisions
        for proj in self.projectiles:
            delete = proj.check_collision_entity(Player_rect)
            # Removes the projectile if it collides withthe player and applies damage to the player
            if delete:
                self.projectiles.remove(proj)
                total_damage += proj.damage
        return total_damage
    #This before checking collision with player
    def check_collision_wall(self,current_level_tiles):
        # Check if any projectiles fired hit a wall
        for proj in self.projectiles:
            delete = proj.check_collision_walls(current_level_tiles)
            # Removes the projectile if it collides with a wall
            if delete:
                self.projectiles.remove(proj)

class Player(Entity):
    def __init__(self,maxhp,name,defence,speed,level,xp,pos):
        # Initialises Player Attributes
        super().__init__(maxhp,name,defence,speed,pos)
        self.Level = level
        self.Experience = xp
        self.respawns = 0
        # Player Abilities and Attributes
        self.Abilities = {"Fire":False,"Wind":False,"Invisible":False}
        self.force_wind = 10
        self.wind_timer = 10000
        self.enemy_burn_damage = 5
        self.fire_timer = 15000
        self.armor_penetration = 0
        self.projectile_speed_increase = 0
        self.ammo_chance = False
        self.slowed_reduced = 0
        self.webbed_reduced = 0
        self.fire_reduced = 0
        self.invisible_duration = 5000
        self.invisible_timer = 20000
        self.healing_kill = False
        self.health_regeneration = False
        
        # Timers for abilities
        self.last_regenerated = -15000
        self.last_hit_time = 0
        self.last_fire_used = -15000
        self.last_wind_used = -10000
        self.last_invisible_used = -20000
        
        # Attack Stats
        self.melee_atk = 0
        self.ranged_atk = 0
        
        # Projectiles list
        self.projectiles = []
        
        # Status Effects
        # Webbed - Traps the enemies for a short time
        # Burning - Does 2 seconds of damage to the player
        # Slowed - Decreases Movement Speed of the player
        # Invisible - One of the players abilities that make them invisible and confuses enemies causing them to not move or attack
        self.Status_Effects = {"Webbed": False,"Slowed": False,"Burning": False,"Invisible": False}
        self.status_effects_last_hit = {"Webbed": 0,"Slowed": 0,"Burning": 0}
        self.last_burn_tick = 0
        
        #Player Avatars
        self.NeutralAvatar = pygame.image.load('Graphics/Player/Neutral.png').convert_alpha()
        self.LeftAvatar = pygame.image.load('Graphics/Player/Left.png').convert_alpha()
        self.RightAvatar = pygame.image.load('Graphics/Player/Right.png').convert_alpha()
        self.UpAvatar = pygame.image.load('Graphics/Player/Up.png').convert_alpha()
        self.CurrentAvatar = self.NeutralAvatar
        self.PlayerRect = self.NeutralAvatar.get_rect(topleft = (self.Position))
        
        self.Ammo = 10
        
        #Movement Tracking
        self.last_pressed_right = False
        self.last_pressed_left = False
        self.last_pressed_up = False
        self.last_pressed_down = False 
        
        # Players Health bar displaying to the user how much health is left
        self.health_bar = HealthBar(500,25,self.MaxHealth)
        # Players XP bar displaying to the user how much xp they have and shows how close they are to levelling uo
        self.xp_bar = Bar(500,12.5,100)
        # Checks if the player should take any damage or not
        self.invincible = True
        
    def check_health_correct(self):
        # Ensures health does not exceed the max health
        if self.Health > self.MaxHealth:
            self.Health = self.MaxHealth
            
    def regeneration(self):
        # Checks if the players health is lower than the max
        if self.Health < self.MaxHealth:
            # Checks the last time health was regenerated if it was more than 15 seconds it regenerates 5 health
            current_time = pygame.time.get_ticks()
            if (current_time - self.last_regenerated) > 15000:
                self.Health += 5
                self.last_regenerated = current_time
                
    def apply_upgrade(self,upgrade):
        # Applies upgrades to player
        match upgrade:
            case "Projectile Speed":
                # Increases Projectile speed
                self.projectile_speed_increase += 0.1
            case "Fire Ability":
                # Player gains fire ability
                self.Abilities["Fire"] = True
            case "Armor Penetration":
                # Player can penetrate through a certain amount of the enemies armour
                self.armor_penetration += 0.1
                # Max amror penetration is 1
                if self.armor_penetration > 1:
                    self.armor_penetration = 1
            case "Wind Ability":
                # Player gains wind ability
                self.Abilities["Wind"] = True
            case "Max Health":
                # Player gains more max health and restores all the health of the player
                self.MaxHealth += 10
                self.health_bar.mv += 10
                self.Health = self.MaxHealth
            case "Healing On Kill":
                # Player gains health as they kill enemies
                self.healing_kill = True
            case "Health Regeneration":
                # Regenerate health every 15 seconds
                self.health_regeneration = True
            case "Slowed Reduced":
                # Reduces the time slowed status effects last
                self.slowed_reduced += 0.1
                if self.slowed_reduced > 1:
                    self.slowed_reduced = 1
            case "Webbed Reduced":
                # Reduces the time webbed status effects last
                self.webbed_reduced += 0.1
                if self.webbed_reduced > 1:
                    self.webbed_reduced = 1
            case "Fire Reduced":
                # Reduces the time fire status effects last
                self.fire_reduced += 0.1
                if self.fire_reduced > 1:
                    self.fire_reduced = 1
            case "Invisible Ability":
                # Reduces the time invisible status effects last
                self.Abilities["Invisible"] = True
            case "Upgrade Wind":
                # Makes the force of the wind ability stronger
                self.force_wind += 10
            case "Upgrade Invisibility":
                # Spend longer invisible
                self.invisible_duration += 2000
            case "Upgrade Fire":
                # Fire damaged does more to enemies
                self.enemy_burn_damage += 5
            case "Fire Cooldown":
                # Fire ability cooldown decreases
                self.fire_timer -= 3000
                if self.fire_timer < 0:
                    self.fire_timer = 3000
            case "Wind Cooldown":
                # Wind ability cooldown decreases
                self.wind_timer -= 3000
                if self.wind_timer < 0:
                    self.wind_timer = 3000
            case "Invisibility Cooldown":
                # Invisinble ability cooldown decreases
                self.invisible_timer -= 3000
                if self.invisible_timer < 0:
                    self.invisible_timer = 3000
            case "Ammo Chance":
                # Chance to not use ammo
                self.ammo_chance = True
            case "Movement Speed":
                # Increases movement speed by 5%
                self.Speed += self.Speed * 0.05
    
    
    def fire_ability(self,enemies_q):
        # Applies fire effect to nearby enemies
        enemies = enemies_q.queue
        radius = 256
        for enemy in enemies:
            if enemy.state == "active":
                # Calculates the distance between the player and the enemy
                distance = math.sqrt((enemy.EnemyRect.x - self.PlayerRect.x)** 2 + (enemy.EnemyRect.y - self.PlayerRect.y) ** 2)
                # Checks if the distance is within the radius of the player
                if distance <= radius:
                    # Makes the player to start burning and take damage
                    enemy.burning[0] = True
                    enemy.burning_damage = self.enemy_burn_damage
                    enemy.burning[1] = pygame.time.get_ticks()
        return enemies

    def wind_ability(self,enemies_q):
        # Pushes away enemies
        enemies = enemies_q.queue
        radius = 256
        for enemy in enemies:
            if enemy.state == "active":
                # Calculates the directional vector from the player to the enemy
                dx = enemy.EnemyRect.x - self.PlayerRect.x
                dy = enemy.EnemyRect.y - self.PlayerRect.y
                distance = math.sqrt((enemy.EnemyRect.x - self.PlayerRect.x)** 2 + (enemy.EnemyRect.y - self.PlayerRect.y) ** 2)
                # Checks if the distance is within the radius of the player
                if distance <= radius:
                    # Normalises the vector so it has a length of 1
                    # Allows for equal push force
                    dx /= distance
                    dy /= distance
                    enemy.wind[0] = True
                    enemy.wind[1] = dx * self.force_wind
                    enemy.wind[2] = dy * self.force_wind
        return enemies
    
    # Shoots Bullets
    def shoot_bullet(self):
        if self.Ammo > 0:
            # Gets the x and y position of the mouse
            x,y = pygame.mouse.get_pos()
            # Gets the x and y position of the player
            player_x,player_y = self.PlayerRect.center
            # Creates a bullet object
            bullet_obj = Bullet(player_x,player_y,x,y,'Graphics/Bullet/BulletA1.png',self.ranged_atk)
            # Applies any projectile speed increase
            bullet_obj.step += bullet_obj.step* self.projectile_speed_increase
            # Adds projectile to list
            self.projectiles.append(bullet_obj)
            # Checks if there is a chance to no consume ammo
            if self.ammo_chance:
                random_no = random.randint(1,5)
                if random_no != 2:
                    self.Ammo -= 1
            else:
                self.Ammo -= 1
            
    def LevelUp(self):
        # Once the player gains 100 or more xp, level increases by 1 and return True
        if self.Experience >= 100:
            self.Experience -= 100
            self.Level += 1
            return True

    def check_status_effects(self,enemy):
        # Checks all the status effects and stores when the player was last hit with it
        if (enemy.Name == "Spider" or enemy.Name == "Spider Boss") and not(self.Status_Effects["Webbed"]):
            self.Status_Effects["Webbed"] = True
            self.status_effects_last_hit["Webbed"] = pygame.time.get_ticks()
        if enemy.Name == "Water" or enemy.Name == "Water Boss" and not(self.Status_Effects["Slowed"]):
            self.Status_Effects["Slowed"] = True
            self.status_effects_last_hit["Slowed"] = pygame.time.get_ticks()
        if (enemy.Name == "Fire" or enemy.Name == "Fire Boss") and not(self.Status_Effects["Burning"]):
            self.Status_Effects["Burning"] = True
            self.status_effects_last_hit["Burning"] = pygame.time.get_ticks()
                 
    def apply_status_effects(self):
        # Applies status effects to the player and checks when the status effects ends and removes it
        if self.Status_Effects["Webbed"]:
            self.Speed = 0
            self.check_time_status_effects("Webbed")
        else:
            self.Speed = 5
        if self.Status_Effects["Slowed"]:
            self.Speed = 2
            self.check_time_status_effects("Slowed")
        else:
            self.Speed = 5
        if self.Status_Effects["Burning"]:
            current_time = pygame.time.get_ticks()
            if (current_time - self.last_burn_tick) >= 1000:
                self.Health -= 5
                self.check_time_status_effects("Burning")
                self.last_burn_tick = current_time
        if self.Status_Effects["Invisible"]:
            current_time = pygame.time.get_ticks()
            self.CurrentAvatar.set_alpha(100)
            self.check_time_status_effects("Invisible")
        if not(self.Status_Effects["Invisible"]):
            self.CurrentAvatar.set_alpha(255)
            
    def check_time_status_effects(self,effect):
        # Checks a status effect for the time left and returns the status of the player back to normal if enough time has passed
        duration = 0
        current_time = pygame.time.get_ticks()
        if effect == "Webbed":
            duration = 500
            duration -= duration * self.webbed_reduced
            last_hit = self.status_effects_last_hit[effect]
            if (current_time - last_hit) >= duration:
                self.Status_Effects[effect] = False
                self.Speed = 5
        if effect == "Slowed":
            duration = 1000
            duration -= duration * self.slowed_reduced
            last_hit = self.status_effects_last_hit[effect]
            if (current_time - last_hit) >= duration:
                self.Status_Effects[effect] = False
                self.Speed = 5
        if effect == "Burning":
            duration = 2000
            duration -= duration * self.fire_reduced
            last_hit = self.status_effects_last_hit[effect]
            if (current_time - last_hit) >= duration:
                self.Status_Effects[effect] = False
        if effect == "Invisible":
            if (current_time - self.last_invisible_used) >= self.invisible_duration:
                self.Status_Effects[effect] = False
                
    def render_player_bars(self):
        #Renders the player health bar and xp bar
        self.health_bar.render(screen,self.Health,0,990)
        self.xp_bar.render(screen,self.Experience,0,990,"blue","gray")
    
    def GainXP(self,amount):
        # Player gains the amount inputted of XP
        self.Experience += amount
    
    def Move(self,current_map):
        # The directs pressed by the player is checked
        moving_right,moving_left,moving_up,moving_down = self.player_inputs()
        movement_player = [0,0]
        #Avatar is changed depending on what was pressed
        if self.last_pressed_left:
            self.CurrentAvatar = self.LeftAvatar
        if self.last_pressed_down:
            self.CurrentAvatar = self.NeutralAvatar
        if self.last_pressed_right:
            self.CurrentAvatar = self.RightAvatar
        if self.last_pressed_up:
            self.CurrentAvatar = self.UpAvatar
        # Adds movement depending on the directon
        if moving_right:
            self.last_pressed_right = True
            self.last_pressed_left = False
            self.last_pressed_up = False
            self.last_pressed_down = False 
            movement_player[0] += self.Speed
            moving_right = False
        if moving_left:
            self.last_pressed_right = False
            self.last_pressed_left = True
            self.last_pressed_up = False
            self.last_pressed_down = False
            movement_player[0] -= self.Speed
            moving_left = False
        if moving_up:
            self.last_pressed_right = False
            self.last_pressed_left = False
            self.last_pressed_up = True
            self.last_pressed_down = False
            movement_player[1] -= self.Speed
            moving_up = False
        if moving_down:
            self.last_pressed_right = False
            self.last_pressed_left = False
            self.last_pressed_up = False
            self.last_pressed_down = True
            movement_player[1] += self.Speed
            moving_down = False
        # Applies the movement to the player
        if not(self.Status_Effects["Webbed"]):
            self.move_player(movement_player,current_map)
        
    def move_player(self, movement, tiles):
        # Moves to the right or left depending if movement is negative or positive
        self.PlayerRect.x += movement[0]
        # Checks collisions in the horizontal directions and makes sure the player does not go outside the walls
        collided_tiles = self.collision_test(tiles)
        for tile in collided_tiles:
            if movement[0] > 0:
                #Right
                self.PlayerRect.right = tile.left
            if movement[0] < 0:
                #Left
                self.PlayerRect.left =tile.right
        # Moves up or down depending if movement is negative or positive
        self.PlayerRect.y += movement[1]
        # Checks collisions in the vertical directions and makes sure the player does not go outside the walls
        collided_tiles = self.collision_test(tiles)
        for tile in collided_tiles:
            if movement[1] > 0:
                #Down
                self.PlayerRect.bottom = tile.top
            if movement[1] < 0:
                #Up
                self.PlayerRect.top = tile.bottom    
    
    def player_inputs(self):
        # Takes the input of hte players
        r = False
        l = False
        u = False
        d = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            l = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            r = True
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            u = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            d = True
        return r,l,u,d
    
    def collision_test(self,tile_rects):
        # Checked if the player collides with tile rects
        collisioned_tiles = []
        for tile in tile_rects:
            if tile.colliderect(self.PlayerRect):
                collisioned_tiles.append(tile)
        return collisioned_tiles
    
    def player_reset(self):
        # Resets the player in a certain position
        self.PlayerRect.x = 925
        self.PlayerRect.y = 440
        self.invincible = True
        self.last_hit_time = pygame.time.get_ticks()
        for effect in self.Status_Effects:
            if effect != "Invisible":
                self.Status_Effects[effect] = False
                self.status_effects_last_hit[effect] = 0
                self.last_burn_tick = 0
        
    
    def render(self,current_level_tiles):
        # Renders the avatar of the player and moves the player avatar
        screen.blit(self.CurrentAvatar,self.PlayerRect)
        self.Move(current_level_tiles)
    
    def check_if_invincible(self,inv_duration):
        # Checks if the player is invincible
        current_time = pygame.time.get_ticks()
        if self.invincible and ((current_time - self.last_hit_time) >= inv_duration):
            self.invincible = False

class Level:
    def __init__(self,maximum_rooms,grid_w, grid_h,start,difficulty):
        self.difficulty = difficulty
        self.start = start # Start position for the random walk algorithm
        self.boss_room_pos = None # Stores the position of the boss room
        self.grid, self.room_pos = self.final(maximum_rooms-1, grid_w, grid_h,start) # Sotres the grid layout of rooms and all the grid position of the rooms
        self.room_pos.insert(0,start) # Adds the node of the start position to the room positions
        self.dict_rooms_empty = self.array_to_dictionary()
        self.dir_rooms = self.find_rooms_around()
        self.chest_opened_pos = []
        #0
        self.basic_walls = pygame.image.load('Graphics/Level/Basic Wall.png').convert_alpha()
        #1
        self.brick_floor = pygame.image.load('Graphics/Level/Brick Floor.png').convert_alpha()
        #2
        self.door = pygame.image.load('Graphics/Level/Door.png').convert_alpha()
        #3
        self.boss_walls = pygame.image.load('Graphics/Level/Boss Wall.png').convert_alpha()
        #4
        self.boss_floor = pygame.image.load('Graphics/Level/Boss Floor.png').convert_alpha()
        #5
        self.treasure_floor = pygame.image.load('Graphics/Level/Treasure Floor.png').convert_alpha()
        #6
        self.chest_open = pygame.image.load('Graphics/Level/Treasure Chest Open.png').convert_alpha()
        self.chest_closed = pygame.image.load('Graphics/Level/Treasure Chest Closed.png').convert_alpha()
        self.chest= self.chest_closed
        self.tile_size_x = 128
        self.tile_size_y = 135
        # Basic room grid layout
        self.basic_room = [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
        [0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
        [0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
        [0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
        [0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
        # Boss room grid layout
        self.boss_room = [
        [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],
        [3,4,4,4,4,4,4,4,4,4,4,4,4,4,3],
        [3,4,4,4,4,4,4,4,4,4,4,4,4,4,3],
        [3,4,4,4,4,4,4,4,4,4,4,4,4,4,3],
        [3,4,4,4,4,4,4,4,4,4,4,4,4,4,3],
        [3,4,4,4,4,4,4,4,4,4,4,4,4,4,3],
        [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]]
        # Treasure room grid layout
        self.treasure_room = [
        [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],
        [3,5,5,5,5,5,5,5,5,5,5,5,5,5,3],
        [3,5,5,5,5,5,5,5,5,5,5,5,5,5,3],
        [3,5,5,5,5,5,5,6,5,5,5,5,5,5,3],
        [3,5,5,5,5,5,5,5,5,5,5,5,5,5,3],
        [3,5,5,5,5,5,5,5,5,5,5,5,5,5,3],
        [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]]
          
    def randomly_select(self):
        #Used to randomly select a direction (left,right,up and down)
        random_number = random.randint(1,4)
        if random_number == 1:
            #Left
            return [-1,0]
        if random_number == 2:
            #Right
            return [1,0]
        if random_number == 3:
            #Down
            return [0,-1]
        if random_number == 4:
            #Up
            return [0,1]
    
    def render(self,tile_map):
        # Renders the level depending on the grid inputted
        screen.fill("black")
        tile_rects_walls = []
        door_rects = []
        chest = False
        # Y corresponds to the y position that is multiplied by the y tile size to place the tile on the correct y position
        y = 0
        for row in tile_map:
            # X corresponds to the x position that is multiplied by the x tile size to place the tile on the correct x position
            x = 0
            for tile in row:
                # Renders depending on the number the tile is and creates a rect used for collisions when rendering the walls
                if tile == 0:
                    screen.blit(self.basic_walls,(x * self.tile_size_x,y * self.tile_size_y))
                    tile_rects_walls.append(pygame.Rect(x * self.tile_size_x, y * self.tile_size_y, self.tile_size_x, self.tile_size_y))
                if tile == 1:
                    screen.blit(self.brick_floor,(x * self.tile_size_x,y * self.tile_size_y))
                if tile == 2:
                    screen.blit(self.basic_walls,(x *self.tile_size_x, y*self.tile_size_y))
                    screen.blit(self.door,(x * self.tile_size_x, y * self.tile_size_y))
                    door_rects.append(pygame.Rect(x * self.tile_size_x, y * self.tile_size_y,self.tile_size_x,self.tile_size_y))
                if tile == 3:
                    screen.blit(self.boss_walls,(x * self.tile_size_x, y* self.tile_size_y))
                    tile_rects_walls.append(pygame.Rect(x * self.tile_size_x, y * self.tile_size_y, self.tile_size_x, self.tile_size_y))
                if tile == 4:
                    screen.blit(self.boss_floor,(x * self.tile_size_x, y * self.tile_size_y))
                if tile == 5:
                    screen.blit(self.treasure_floor,(x * self.tile_size_x, y * self.tile_size_y))
                if tile == 6:
                    screen.blit(self.treasure_floor,(x * self.tile_size_x, y * self.tile_size_y))
                    screen.blit(self.chest,(x * self.tile_size_x, y * self.tile_size_y))
                    chest_rect = pygame.Rect(x * self.tile_size_x, y * self.tile_size_y, self.tile_size_x, self.tile_size_y)
                    chest = True
                # Increments x by one to move render position to the right
                x += 1
            # Increments y by one to move render position down by 1
            y += 1
        # If there is a chest then a chest rect is returned along with the tile and door rects
        if chest:
            return tile_rects_walls,door_rects,chest_rect
        else:
            return tile_rects_walls,door_rects

    def basic_room_render(self):
        # Renders a basic room
        basic_walls_rects,door_rects = self.render(self.basic_room)
        return basic_walls_rects,door_rects

    def boss_room_render(self):
        # Renders a boss room
        boss_walls_rects,door_rects  = self.render(self.boss_room)
        return boss_walls_rects,door_rects 
    
    def treasure_room_render(self):
        # Renders a treasure room
        treasure_walls_rects,door_rects,chest_rect = self.render(self.treasure_room)
        return treasure_walls_rects,door_rects,chest_rect
    
    def create(self,maximum_rooms, grid_w,grid_h,start):
        # Create random rooms based off the start point
        room_pos = []
        grid = [
               [0,0,0,0,0,0,0,0,0],
               [0,0,0,0,0,0,0,0,0],
               [0,0,0,0,1,0,0,0,0],
               [0,0,0,0,0,0,0,0,0],
               [0,0,0,0,0,0,0,0,0]
               ]
        # A boolean grid that stores visited 
        visited_grid = [[False,False,False,False,False,False,False,False,False],
            [False,False,False,False,False,False,False,False,False],
            [False,False,False,False,True,False,False,False,False],
            [False,False,False,False,False,False,False,False,False],
            [False,False,False,False,False,False,False,False,False]]
        # While loop that continues untill all rooms have been added 
        while maximum_rooms != 0:
            v = True
            # Checks if the room is valid 
            while v:
                new_start = [0,0]
                direction = self.randomly_select()
                # Changes the start and stores it in a new variable depending on the direction
                new_start[0] = start[0] + direction[0]
                new_start[1] = start[1] + direction[1]
                # Checks if the start is within range of the grid
                if (new_start[0] < grid_h and new_start[0] > -1) and (new_start[1] < grid_w and new_start[1] > -1):
                    v = False
            # Changes the old start to position to the new room that was made
            start = new_start
            # Checks to see if the room is visited or not
            cell = visited_grid[start[0]][start[1]]
            if not(cell):
                # If the room is not visited then in the boolean grid that position is made to be true
                visited_grid[start[0]][start[1]] = True
                # A room is added to the grid and the position of the room is added to room_pos
                grid[start[0]][start[1]] = 1
                room_pos.append(start)
                # Decreases the number of room left by 1
                maximum_rooms -= 1
        return room_pos,grid
    
    def random_level(self):
        # Picks a random number of rooms depending on the difficulty chosen
        if self.difficulty == "Easy":
            no_treasure = random.randint(1,2)
        if self.difficulty == "Medium":
            no_treasure = random.randint(2,4)
        if self.difficulty == "Hard":
            no_treasure = random.randint(1,4)
        return no_treasure
    
    def boss_placement(self,start,grid_w,grid_h,grid):
        # Places the boss room as far away as possible from the start room
        start_row = start[0]
        start_col = start[1]
        max_distance = -1
        furthest_cell = []
        
        for row in range(grid_h):
            for column in range(grid_w):
                # Checks to see where there are rooms
                if grid[row][column] == 1:
                    #Manhattan distance checks the distance between 2 points if you were to travel along the x axis and then along the y axis
                    # Abs function is used to make sure the calculation is positive and gets only the magnitude of distance
                    distance = abs(row-start_row) + abs(column - start_col)
                    # if the distance is greater than the max distance
                    if distance > max_distance:
                        # Makes distance become the max distance as this is the current furthest room/distance that has been found so far
                        max_distance = distance
                        # Gets the position of the furthest room found
                        furthest_cell = [row,column]
        # Once loop has complete and the furthest cell has been found the room becomes a 3(boss room)
        grid[furthest_cell[0]][furthest_cell[1]] = (3)
        # Stores the boss room position in the grid
        self.boss_room_pos = (furthest_cell[0],furthest_cell[1])
        return furthest_cell
    
    def final(self,maximum_rooms, grid_w, grid_h,start):
        # Create the rooms randomly
        room_pos, grid = self.create(maximum_rooms,grid_w,grid_h,start)
        # Places the boss room
        boss_room = self.boss_placement(start,grid_w,grid_h,grid)
        treasure_counter = 0 # Number of treasure rooms placed
        no_treasure = self.random_level()
        # Chosen stores the rooms that have been selected and the boss room is placed in there by default to prevent it from being changed
        chosen = [boss_room]
        # A while loop where rooms are changd until the number of treasure rooms in the grid is met
        while no_treasure != treasure_counter:
            # Selects a random room position
            room_selected = room_pos[random.randint(0,maximum_rooms-1)]
            place = True
            # Checks if the room has already been chosen
            for room in chosen:
                # If a room has been chosen then place is made false meaning to not place a treasure room
                if room_selected == room:
                    place = False
            # If the room has not been chosen
            if place:
                # a treasure room is placed on the grid and replaces the room
                grid[room_selected[0]][room_selected[1]]= (2)
                # Adds chosen to list to make sure the room doesnt get picked again
                chosen.append(room_selected)
                # Treasure counter increases by 1 as there has been a successful placement
                treasure_counter += 1
                    
        return grid,room_pos
    
    def array_to_dictionary(self):
        # Converts the array, room pos to a dictionary
        dict_rooms = {}
        for i in self.room_pos:
            pos = (i[0],i[1])
            dict_rooms[pos] = []
        return dict_rooms
    
    def find_rooms_around(self):
        #Check for any neighbouring rooms

        # Converts room pos into a dictionary
        dict_rooms = self.array_to_dictionary()
        # For loop to go through each room position
        for room in self.room_pos:
            # Gets the x and y of the current room position it is looking at
            y = room[0]
            x = room[1]
            # Gets the x and y of potential neighbouring rooms
            neighbour_u = (y-1,x)
            neighbour_d = (y+1,x)
            neighbour_l = (y,x-1)
            neighbour_r = (y,x+1)
            correct_neighbours = [] # Stores the direction of neighbours in correspondance to the room being looked at
            # For loop that checks through each room position again
            for room_2 in self.room_pos:
                # Gets the x and y of each room
                room_x = room_2[1]
                room_y = room_2[0]
                # Checks to see if any of the potential neighbours are real room on the grid
                if neighbour_l[1] == room_x  and neighbour_l[0] == room_y:
                    # Left room valid
                    correct_neighbours.append("left")
                elif neighbour_r[1] == room_x and neighbour_r[0] == room_y:
                    # Right room valid
                    correct_neighbours.append("right")
                elif neighbour_u[1] == room_x and neighbour_u[0] == room_y:
                    # Up room valid
                    correct_neighbours.append("up")
                elif neighbour_d[1] == room_x and neighbour_d[0] == room_y:
                    # Down room valid
                    correct_neighbours.append("down")
            # Appends all the directions there are rooms a certain room
            dict_rooms[(y,x)] = correct_neighbours
        return dict_rooms
    
    def determine_door_direction(self,current):
        # Gets the current room, checking for directions and changes the rendering of a room to add doors
        current_room = self.grid[current[0]][current[1]]
        
        # Checks room for directions
        for direction in self.dir_rooms[current]:
            # Changes either basic, treasure and boss room and adds doors 
            if direction == "left":
                #Basic room
                if current_room == 1:
                    self.basic_room[3][0] = 2
                #Tresure room    
                if current_room == 2:
                    self.treasure_room[3][0] = 2
                #Boss room   
                if current_room == 3:
                    self.boss_room[3][0] = 2

            if direction == "right":
                #Basic room
                if current_room == 1:
                    self.basic_room[3][14] = 2

                #Tresure room    
                if current_room == 2:
                    self.treasure_room[3][14] = 2

                #Boss room   
                if current_room == 3:
                    self.boss_room[3][14] = 2
            if direction == "up":
                #Basic room
                if current_room == 1:
                    self.basic_room[0][7] = 2

                #Tresure room    
                if current_room == 2:
                    self.treasure_room[0][7] = 2

                #Boss room   
                if current_room == 3:
                    self.boss_room[0][7] = 2

            if direction == "down":
                #Basic room
                if current_room == 1:
                    self.basic_room[6][7] = 2
 
                #Tresure room    
                if current_room == 2:
                    self.treasure_room[6][7] = 2

                #Boss room   
                if current_room == 3:
                    self.boss_room[6][7] = 2
    
    def reset_all_rooms(self,current_room_pos):
        # Resets any changes done to the rooms and restores back to how they were without any doors
        self.basic_room[3][0] = 0
        self.basic_room[3][14] = 0
        self.basic_room[0][7] = 0
        self.basic_room[6][7] = 0
        self.treasure_room[3][0] = 3
        self.treasure_room[3][14] = 3
        self.treasure_room[0][7] = 3
        self.treasure_room[6][7] = 3
        # Makes sure the chest is correctly opened or closed
        self.chest = self.chest_closed
        for pos in self.chest_opened_pos:
            if pos == current_room_pos:
                self.chest = self.chest_open
        self.boss_room[3][0] = 3
        self.boss_room[3][14] = 3
        self.boss_room[0][7] = 3
        self.boss_room[6][7] = 3
      
class Queue:
    def __init__(self,size):
        self.queue = [None] * size # Creates an array of a certain size
        self.FP = 0 # Front pointer
        self.BP = -1 # Back pointer
    
    def Enqueue(self,item):
        # Adds an item to the queue
        self.BP = self.BP + 1 # Increments back pointer by 1
        # Checks if the BP is less than the length of the queue
        if self.BP < len(self.queue):
            # Changes the element at the index of the BP to an item
            self.queue[self.BP] = item
    def IsEmpty(self):
        # Checks if the queue is empty or not
        # If the front pointer is larger than the rear pointer then that means something is in the queue
        if self.FP > self.BP:
            return True
        else:
            return False
    def Dequeue(self):
        # Removes the last item in a queue
        # Checks if the queue is empty or not
        if not(self.IsEmpty()):
            # If it is not empty then item is removed from the queue where the FP is 
            item = self.queue[self.FP]
            self.queue[self.FP] = None
            # Front pointer is incremented by 1
            self.FP = self.FP + 1
            return item

class Menu:
    def __init__(self):
        self.difficulty_chosen = None # Stores what difficulty is chosen
        self.select_saves = None # Stores what save is selected
        self.running = True # Determines if the main menu loop is running or not
        
        # Custom Cursor set up
        self.cursor_image = pygame.transform.scale_by(pygame.image.load('Graphics/Menu Cursor.png').convert_alpha(),3)
        self.cursor = pygame.cursors.Cursor((15,5), self.cursor_image)
    
    def main_menu(self):
        #Renders Main Menu correctly
        # Loads in the graphics needed 
        main_menu_screen = pygame.image.load('Graphics/Menu/Main Menu/Main Menu.png').convert_alpha()
        play_button = pygame.image.load('Graphics/Menu/Main Menu/Play Button.png').convert_alpha()
        instructions_button = pygame.image.load('Graphics/Menu/Main Menu/Instructions Button.png').convert_alpha()
        exit_button = pygame.image.load('Graphics/Menu/Main Menu/Exit Button.png').convert_alpha()
        
        #Creates rects for buttons
        play_button_rect = play_button.get_rect(center = (986,440))
        instructions_button_rect = instructions_button.get_rect(center = (988, 690))
        exit_button_rect = exit_button.get_rect(center = (988,950))
        # Changes the cursor
        pygame.mouse.set_cursor(self.cursor)
        while self.running:
            clicked = False
            # Pygame events 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                # Checks if the mouse was left clicked
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        clicked = True

            # Gets the position of the mouse
            mouse_pos = pygame.mouse.get_pos()
            screen.fill("Black")
            # Render
            screen.blit(main_menu_screen,(0,0))
            screen.blit(play_button,play_button_rect)
            screen.blit(instructions_button,instructions_button_rect)
            screen.blit(exit_button,exit_button_rect)
            
            # Checks if the the play button was clicked
            if play_button_rect.collidepoint(mouse_pos):
                if clicked:
                    # Checks if a save was available by checking if file names exist
                    save_available = False
                    for i in range(1,4):
                        file_exist = os.path.isfile(f'Game{i}.db')
                        if file_exist:
                            save_available = True
                    if save_available:
                        # If a save was available a screen would appear to give the user an option of starting a new game or loading a game
                        new,load = self.new_or_load()
                        if new:
                            # If a new game was chosen then they would be sent to choose a difficulty
                            self.difficulty_chosen = self.difficulty_menu()
                            self.running = False
                        if load:
                            # If they chose to load a save then they would be able to select save slots 1,2,3 depending on where things were saved
                            self.select_saves = self.select_save()
                            self.running = False
                    else:
                        # If not save was available then they would be taken straight to a difficulty screen
                        self.difficulty_chosen = self.difficulty_menu()
                        self.running = False
            if instructions_button_rect.collidepoint(mouse_pos):
                if clicked:
                    self.instructions_menu()
            #Quits the program
            if exit_button_rect.collidepoint(mouse_pos):
                # Exits the game
                if clicked:
                    pygame.quit()
                    exit()
            
            pygame.display.update()
            clock.tick(60)
            
    def instructions_menu(self):
        #Gives an explanation of what to do in the game
        running = True
        # Graphics loaded
        display_screen = pygame.image.load('Graphics/Menu/How To Play/how to play.png').convert_alpha()
        while running:
            # Pygame Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            #Render
            screen.blit(display_screen,(0,0))
            
            pygame.display.update()
            clock.tick(60)
    def difficulty_menu(self):
        #Renders Difficulty menu selection
        running = True
        #Gets the average of each difficulty
        load = Load("Score")
        Scores = load.load_score_difficulty()
        easy_average = int(Scores["Easy"])
        medium_average = int(Scores["Medium"])
        hard_average = int(Scores["Hard"])
        # Loads in graphics needed
        difficulty_screen = pygame.image.load('Graphics/Menu/Difficulty Screen/idle state.png').convert_alpha()
        easy_screen = pygame.image.load('Graphics/Menu/Difficulty Screen/easy.png').convert_alpha()
        medium_screen = pygame.image.load('Graphics/Menu/Difficulty Screen/medium.png').convert_alpha()
        hard_screen = pygame.image.load('Graphics/Menu/Difficulty Screen/hard.png').convert_alpha()
        font = pygame.font.Font('Fonts/Montserrat-Bold.ttf',50)
        while running:
            clicked = False
            # Pygame Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                # Checks if the mouse was left clicked
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        clicked = True
            
            # Gets the position of the mouse
            mouse_pos = pygame.mouse.get_pos()
            
            # Renders
            screen.blit(difficulty_screen,(0,0))
            
            # Checks what difficulty was clicked
            if mouse_pos[0] >= 855 and mouse_pos[0]<= 1080 and mouse_pos[1] > 240 and mouse_pos[1] < 301:
                screen.blit(easy_screen,(0,0))
                if easy_average > 0:
                    #Renders easy average score
                    text = font.render(f'Easy Average Score: {easy_average}',True,"White")
                    screen.blit(text,(625,20))
                if clicked:
                    difficulty_chosen = "Easy"
                    running = False
            if mouse_pos[0] >= 775 and mouse_pos[0]<= 1165 and mouse_pos[1] > 500 and mouse_pos[1] < 555:
                screen.blit(medium_screen,(0,0))
                if medium_average > 0:
                    #Renders medium average score
                    text = font.render(f'Medium Average Score: {medium_average}',True,"White")
                    screen.blit(text,(575,20))
                if clicked:
                    difficulty_chosen = "Medium"
                    running = False
                
            if mouse_pos[0] >= 840 and mouse_pos[0]<= 1095 and mouse_pos[1] > 760 and mouse_pos[1] < 820:
                screen.blit(hard_screen,(0,0))
                if hard_average > 0:
                    #Renders hard average score
                    text = font.render(f'Hard Average Score: {hard_average}',True,"White")
                    screen.blit(text,(625,20))
                if clicked:
                    difficulty_chosen = "Hard"
                    running = False
            pygame.display.update()
            clock.tick(60)
        return difficulty_chosen

    def new_or_load(self):
        #Renders selection screen between new game or load game
        running = True
        # Loads in graphics needed
        new_load_screen = pygame.image.load('Graphics/Menu/New or Load Screen/New Load.png').convert_alpha()
        new_game = False # Shows if the player has selected new game
        load = False # Shows if the player has selected load game
        start_time = pygame.time.get_ticks() # Time when this game screen started

        while running:
            clicked = False
            # Pygame Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                # Checks if the mouse was left clicked
                if event.type == pygame.MOUSEBUTTONUP:
                    current_time = pygame.time.get_ticks()
                    # Waits until half a second has passed to register a click to make sure no accidental presses happens inbetween menus
                    if event.button == 1 and ((current_time-start_time) > 500):
                        clicked = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            #Gets the mouse position
            mx,my = pygame.mouse.get_pos()
            #Fills the screen with black to make sure previous renders are not shown
            screen.fill("Black")
            # Render
            screen.blit(new_load_screen,(0,0))
            #Checks to see if new game or load was pressed
            if clicked:
                if mx >= 410 and mx <= 1550:
                    # New game selected
                    if my >= 120 and my <= 420:
                        new_game = True
                        running = False
                    # Load game selected
                    if my >= 560 and my <= 860:
                        load = True
                        running = False
            pygame.display.update()
            clock.tick(60)
        return new_game,load
    
    def select_save(self):
        #Renders save selection 
        running = True
        # Graphics needed is loaded
        new_load_screen = pygame.image.load('Graphics/Menu/background.png').convert_alpha()
        save_1_surface = pygame.image.load('Graphics/Menu/Save Screen/Save1.png').convert_alpha()
        save_1_rect= save_1_surface.get_rect(topleft = (610.3,134.3))
        save_2_surface = pygame.image.load('Graphics/Menu/Save Screen/Save2.png').convert_alpha()
        save_2_rect= save_2_surface.get_rect(topleft = (610.3,399))
        save_3_surface = pygame.image.load('Graphics/Menu/Save Screen/Save3.png').convert_alpha()
        save_3_rect= save_3_surface.get_rect(topleft = (610.3,661.4))
        save_selected = {"Save 1": False,"Save 2": False,"Save 3": False}
        saves_available = {"Save 1": os.path.isfile(f'Game{1}.db'),"Save 2": os.path.isfile(f'Game{2}.db'), "Save 3": os.path.isfile(f'Game{3}.db')}
        start_time = pygame.time.get_ticks() # Time when this game screen started
        while running:
            clicked = False
            # Pygame Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                # Checks if the mosue was left clicked
                if event.type == pygame.MOUSEBUTTONUP:
                    current_time = pygame.time.get_ticks()
                    # Waits until half a second has passed to register a click to make sure no accidental presses happens inbetween menus
                    if event.button == 1 and ((current_time-start_time) > 500):
                        clicked = True
            # Gets the mouse position
            mx,my = pygame.mouse.get_pos()
            # Render
            screen.fill("Black")
            screen.blit(new_load_screen,(0,0))
            # Renders depending on the save available
            if saves_available["Save 1"]:
                screen.blit(save_1_surface,save_1_rect)
            if saves_available["Save 2"]:
                screen.blit(save_2_surface,save_2_rect)
            if saves_available["Save 3"]:
                screen.blit(save_3_surface,save_3_rect)
            # Checks which save was clicked
            if clicked:
                if save_1_rect.collidepoint(mx,my):
                    save_selected["Save 1"] = True
                    running = False
                if save_2_rect.collidepoint(mx,my):
                    save_selected["Save 2"] = True
                    running = False
                if save_3_rect.collidepoint(mx,my):
                    save_selected["Save 3"] = True
                    running = False
            pygame.display.update()
            clock.tick(60)
        return save_selected
    
    def death_screen(self):
        # Renders the death screen
        running = True
        clicked = False
        # Graphics are loaded
        background = pygame.image.load('Graphics/Menu/Death Screen/Dead background.png').convert_alpha()
        respawn_surface = pygame.image.load('Graphics/Menu/Death Screen/Respawn.png').convert_alpha()
        respawn_rect= respawn_surface.get_rect(topleft = (611,223.2))
        save_surface = pygame.image.load('Graphics/Menu/Death Screen/Save.png').convert_alpha()
        save_rect= save_surface.get_rect(topleft = (611,487.9))
        exit_surface = pygame.image.load('Graphics/Menu/Death Screen/Exit.png').convert_alpha()
        exit_rect= exit_surface.get_rect(topleft = (611,750.3))
        # Selected buttons
        selected = {"Respawn":False, "Save": False,"Exit":False}
        start_time = pygame.time.get_ticks()
        while running:
            # Pygame Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                # Checks if the mouse was left clicked
                if event.type == pygame.MOUSEBUTTONUP:
                    current_time = pygame.time.get_ticks()
                    # Waits until half a second has passed to register a click to make sure no accidental presses happens inbetween menus
                    if event.button == 1 and ((current_time-start_time) > 500):
                        clicked = True

            #Gets the mouse position
            mx,my = pygame.mouse.get_pos()
            #Fills the screen with black to make sure previous renders are not shown
            screen.fill("Black")
            # Render
            screen.blit(background,(0,0))
            screen.blit(respawn_surface,respawn_rect)
            screen.blit(save_surface,save_rect)
            screen.blit(exit_surface,exit_rect)
            if clicked:
                if respawn_rect.collidepoint(mx,my):
                    selected["Respawn"] = True
                    running = False
                if save_rect.collidepoint(mx,my):
                    selected["Save"] = True
                    running = False
                if exit_rect.collidepoint(mx,my):
                    selected["Exit"] = True
                    running = False
            pygame.display.update()
            clock.tick(60)
        return selected
    
    def pause_screen(self):
        # Renders the pause screen
        running = True
        clicked = False
        # Graphics are loaded
        background = pygame.image.load('Graphics/Menu/background.png').convert_alpha()
        play_surface = pygame.image.load('Graphics/Menu/Pause Screen/Play.png').convert_alpha()
        play_rect= play_surface.get_rect(topleft = (610.3,134.3))
        save_surface = pygame.image.load('Graphics/Menu/Pause Screen/Save.png').convert_alpha()
        save_rect= save_surface.get_rect(topleft = (610.3,399))
        exit_surface = pygame.image.load('Graphics/Menu/Pause Screen/Exit.png').convert_alpha()
        exit_rect= exit_surface.get_rect(topleft = (610.3,661.4))
        # Selected buttons
        selected = {"Play":False, "Save": False,"Exit":False}
        start_time = pygame.time.get_ticks()
        while running:
            # Pygame Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                # Checks if the mouse was left clicked
                if event.type == pygame.MOUSEBUTTONUP:
                    current_time = pygame.time.get_ticks()
                    # Waits until half a second has passed to register a click to make sure no accidental presses happens inbetween menus
                    if event.button == 1 and ((current_time-start_time) > 500):
                        clicked = True
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        selected["Play"] = True
                        running = False
            #Gets the mouse position
            mx,my = pygame.mouse.get_pos()
            #Fills the screen with black to make sure previous renders are not shown
            screen.fill("Black")
            # Render
            screen.blit(background,(0,0))
            screen.blit(play_surface,play_rect)
            screen.blit(save_surface,save_rect)
            screen.blit(exit_surface,exit_rect)
            #Checks to see if play, save or exit was pressed
            if clicked:
                if play_rect.collidepoint(mx,my):
                    selected["Play"] = True
                    running = False
                if save_rect.collidepoint(mx,my):
                    selected["Save"] = True
                    running = False
                if exit_rect.collidepoint(mx,my):
                    selected["Exit"] = True
                    running = False
            
            pygame.display.update()
            clock.tick(60)
        return selected 
    
    def save_screen(self):
        #Renders saving screen
        running = True
        # Graphics are loaded
        new_load_screen = pygame.image.load('Graphics/Menu/background.png').convert_alpha()
        save_1_surface = pygame.image.load('Graphics/Menu/Save Screen/Save1.png').convert_alpha()
        save_1_rect= save_1_surface.get_rect(topleft = (610.3,134.3))
        save_2_surface = pygame.image.load('Graphics/Menu/Save Screen/Save2.png').convert_alpha()
        save_2_rect= save_2_surface.get_rect(topleft = (610.3,399))
        save_3_surface = pygame.image.load('Graphics/Menu/Save Screen/Save3.png').convert_alpha()
        save_3_rect= save_3_surface.get_rect(topleft = (610.3,661.4))
        # Selected buttons
        save_selected = {"Save 1": False,"Save 2": False,"Save 3": False}
        start_time = pygame.time.get_ticks()
        while running:
            clicked = False
            # Pygame Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                # Checks if the mouse was left clicked
                if event.type == pygame.MOUSEBUTTONUP:
                    current_time = pygame.time.get_ticks()
                    # Waits until half a second has passed to register a click to make sure no accidental presses happens inbetween menus
                    if event.button == 1 and ((current_time-start_time) > 500):
                        clicked = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            #Gets the mouse position
            mx,my = pygame.mouse.get_pos()
            #Fills the screen with black to make sure previous renders are not shown
            screen.fill("Black")
            # Render
            screen.blit(new_load_screen,(0,0))
            screen.blit(save_1_surface,save_1_rect)
            screen.blit(save_2_surface,save_2_rect)
            screen.blit(save_3_surface,save_3_rect)
            #Checks to see what save slot was selected
            if clicked:
                if save_1_rect.collidepoint(mx,my):
                    save_selected["Save 1"] = True
                    running = False
                if save_2_rect.collidepoint(mx,my):
                    save_selected["Save 2"] = True
                    running = False
                if save_3_rect.collidepoint(mx,my):
                    save_selected["Save 3"] = True
                    running = False
            pygame.display.update()
            clock.tick(60)
        return save_selected
    
    def win_screen(self,score):
        # Renders the win screen
        running = True
        clicked = False
        # Graphics are loaded
        background = pygame.image.load('Graphics/Menu/Win Screen/Win Background.png').convert_alpha()
        main_menu_surface = pygame.image.load('Graphics/Menu/Win Screen/Main Menu Button.png').convert_alpha()
        main_menu_rect = main_menu_surface.get_rect(topleft = (339.6,533.5))
        start_time = pygame.time.get_ticks()
        font = pygame.font.Font('Fonts/Cinzel.ttf',200)
        score_text = font.render(f'SCORE: {score}',True,"White")
        while running:
            clicked = False
            # Pygame Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                # Checks if the mouse was left clicked
                if event.type == pygame.MOUSEBUTTONUP:
                    current_time = pygame.time.get_ticks()
                    # Waits until half a second has passed to register a click to make sure no accidental presses happens inbetween menus
                    if event.button == 1 and ((current_time-start_time) > 500):
                        clicked = True
            
            #Gets the mouse position
            mx,my = pygame.mouse.get_pos()
            #Fills the screen with black to make sure previous renders are not shown
            screen.fill("Black")
            # Render
            screen.blit(background,(0,0))
            screen.blit(main_menu_surface,main_menu_rect)
            screen.blit(score_text,(380,240))
            #Checks to see if new game or load was pressed
            if clicked:
                if main_menu_rect.collidepoint(mx,my):
                    running = False
            pygame.display.update()
            clock.tick(60)  
           
class Pathfinding:
    def __init__(self,graph):
        # Takes in a graph/adjacency matrix
        self.graph = graph
    
    def bfs_pathfinding(self,graph,start,final):
        # Traverses all adjacent nodes and then traverses all their adjacent node until destination is reached
        # Creates a queue with size 1000 to prevent crashing
        queue = Queue(1000)
        # Dictionary that stores the paths from the start node to each visited node
        # The start node is the only node in the path
        path = {start: [start]}
        # Adds the start node to the queue
        queue.Enqueue(start)
        # List of visited nodes to prevent repeates
        visited = []
        # While loop lasts until the queue is empty
        while not queue.IsEmpty():
            # Removes and stores the first node in the queue
            current = queue.Dequeue()
            # If the current node is the target node then the path is returned
            if current == final:
                return path[current]
            # If the current node is not in the visited array it is appended
            if current not in visited:
                visited.append(current)
                # Loops through each neighbour of the current node nad checks if it is visited
                for neighbor in graph[current]:
                    if neighbor not in visited:
                        # If it isn't visited it is added to the queue
                        queue.Enqueue(neighbor)
                        # Adds new key of neighbour and extends the path of current
                        path[neighbor] = path[current] +[neighbor]
                        
        return None
    
    def find_index(self,tile_position, tilesize_x,tilesize_y): 
        # Corrosponds the y and x positions to a index on the grid   
        player_x = tile_position[0]
        player_y = tile_position[1]
        grid_x = player_y / tilesize_y
        grid_y = player_x / tilesize_x
        grid_int_x = player_y // tilesize_y
        grid_int_y = player_x // tilesize_x
        rounded_x = self.round(grid_x,grid_int_x)
        rounded_y = self.round(grid_y,grid_int_y)
        index = (rounded_y,rounded_x)
        return index
    
    def round(self,number,int_number):
        # Rounds the a number using the decimal form and the integer form
        decimal = number - int_number
        signif_number = int(str(decimal)[2])
        if signif_number >= 5:
            return int_number + 1
        elif signif_number < 5:
            return int_number

class Bar:
    def __init__(self,w,h,max_value):
        self.width = w # Width of the bar
        self.height = h # Height of the bar
        self.mv = max_value # Max value of the bar
    
    def find_ratio(self,value):
        # Returns a ratio of the value and max value of the bar
        return value / self.mv
    
    def render(self,surface,value,x,y,fg_colour,bg_colour):
        ratio = self.find_ratio(value)
        pygame.draw.rect(surface, f'{bg_colour}', (x,y, self.width, self.height)) # Draws a coloured rectangle to show remainder missing
        pygame.draw.rect(surface, f'{fg_colour}', (x,y, self.width* ratio, self.height)) # Draws a coloured rectangle to show current value
        
class HealthBar(Bar):
    def __init__(self,w,h,max_hp):
        # Inherits from the bar class
        super().__init__(w,h,max_hp)
    
    def render(self,surface,hp,x,y):
        # Renders health bar
        y -= 30 # Displaces health bar up 30 pixels
        ratio = self.find_ratio(hp)
        pygame.draw.rect(surface, "red", (x,y, self.width, self.height)) # Draws a red rectangle to show the health missing
        pygame.draw.rect(surface, "green", (x,y, self.width* ratio, self.height)) # Draws a green rectangle to show current health

class Item():
    def __init__(self,name):
        self.name = name # Name of the item
        self.type = {"Helmet": False,"Chest": False, "Gloves": False,"Boots":False,"Ammo": False,"Primary Weapon": False,"Secondary Weapon": False, "Health Consumable": False} # Item types
        self.materials = {"Adamantite": 9,"Mithril":8,"Golden":7,"Steel":6,"Iron":5,"Silver":4,"Metal":3,"Leather":2,"Wood":1} # Materials with different values showing strength
        self.modifiers = {"Dragon":9,"Enhanced":8,"Ribbed":7,"Beaked":6,"HardStudded":5,"Studded":4,"Hard": 3, "Soft":2,"Rusty":1} # Modifiers with different values showing strength
        self.weight = 3 # Multiplier for materials and modifiers
        self.attack = 0 # Attack of item
        self.defence = 0 # Defence of item
        self.health = 0 # Health of item
        self.equipped = False # Represents if the item is equipped or not
        self.check_type() # Checks what type of item it is
        self.get_attack_defence() # Gets either the attack or defence of the item
        self.rarity = self.get_rarity() # Gets the rarity of the item
        self.give_health() # Gets the health the item would give
    
    
    def check_type(self):
        # Checks the item type
        words = self.name.split() # Splits the name into an array of words
        # For loop that checks each word
        for word in words:
            # Checks if the name contains certain words linking them to an item type
            if word.lower() == "cap" or word.lower() == "hat":
                self.type["Helmet"] = True
            elif word.lower() == "cloak" or word.lower() == "chestplate":
                self.type["Chest"] = True
            elif word.lower() == "gloves":
                self.type["Gloves"] = True
            elif word.lower() == "boots":
                self.type["Boots"] = True
            elif word.lower() == "bow" or word.lower() == "crossbow":
                self.type["Primary Weapon"] = True
            elif word.lower() == "bolt" or word.lower() == "arrow":
                self.type["Ammo"] = True
            elif word.lower() == "food":
                self.type["Health Consumable"] = True
            elif word.lower() == "axe" or word.lower() == "hammer" or word.lower() == "dagger" or word.lower() == "mace":
                self.type["Secondary Weapon"] = True
    
    def give_health(self):
        # If the item is a health consumable, apply a health value to it 
        if self.type["Health Consumable"]:
            words = self.name.split() # Splits the name into an array of words
            for word in words:
                # Checks if the word is mushroom or health and gives a certain value 
                if word.lower() == "mushroom":
                    self.health = 10
                if word.lower() == "health":
                    self.health = 50
            # If the health is 0 then it gives 20 for health
            if self.health == 0:
                self.health = 20
        
    def get_attack_defence(self):
        words = self.name.split() # Splits the name into an array of words
        for word in words:
            # Checks if name contain any modifiers or materials that increase its strength 
            for material in self.materials:
                # Checks if the item is an attack type weapon
                if self.type["Ammo"] or self.type["Primary Weapon"] or self.type["Secondary Weapon"]:
                    if word == material:
                        # Accumulates attack and adds the weight * value of the material
                        self.attack += (self.weight * self.materials[material])
                # Checks if the item is an defence type weapon
                if self.type["Helmet"] or self.type["Chest"] or self.type["Boots"] or self.type["Gloves"]:
                    if word == material:
                        # Accumulates defence and adds the weight * value of the material
                        self.defence += (self.weight * self.materials[material])
            for modifier in self.modifiers:
                    # Checks if the item is an attack type weapon
                    if self.type["Ammo"] or self.type["Primary Weapon"] or self.type["Secondary Weapon"]:
                        if word == modifier:
                            # Accumulates attack and adds the weight * value of the material
                            self.attack += (self.weight * self.modifiers[modifier])
                    # Checks if the item is an defence type weapon
                    if self.type["Helmet"] or self.type["Chest"] or self.type["Boots"]:
                        if word == modifier:
                            # Accumulates defence and adds the weight * value of the material
                            self.defence += (self.weight * self.modifiers[modifier])
        # Checks if the item is an attack type weapon
        if self.type["Ammo"] or self.type["Primary Weapon"] or self.type["Secondary Weapon"]:
            if self.attack == 0:
                # Applies 15 attack if it has no modifier or materials
                self.attack = 15
        # Checks if the item is an defence type weapon
        if self.type["Helmet"] or self.type["Chest"] or self.type["Boots"] or self.type["Gloves"]:
            if self.defence == 0:
                # Applies 10 defence if it has no modifier or materials
                self.defence = 10

    def get_rarity(self):
        # Gets the rarity of the item
        stat = None # Gets the value of the item
        if self.attack > 0:
            stat = self.attack
        if self.defence > 0:
            stat = self.defence
        # If the item is health consumable it is given the common rarity
        # if self.health > 0:
        #     return "Common"
        if stat != None:
            # Depending on the attack or defence a rarity is returned (Common, Uncommon, Rare and Epic)
            if stat >= 3 and stat <=12:
                return "Common"
            if stat >=13 and stat <=20:
                return "Uncommon"
            if stat >= 21 and stat <=30:
                return "Rare"
            if stat >= 31:
                return "Epic"
        return None

class Inventory():
    def __init__(self):
        self.pause = False 
        self.items = [] # Containes all the items the player has in their inventory
        self.max_grid_size = 5 # Max grid width and height displayed to the player
        self.TileSize = 128 # Tile size of inv
        #Rects
        self.grid_rects = [] # Contains all the rects of the grid 
        self.helmet_rect = pygame.Rect(1536,158,self.TileSize *1.5 ,self.TileSize *1.5)
        self.chest_rect = pygame.Rect(1505,356,self.TileSize *2 ,self.TileSize *3)
        self.gloves_rect = pygame.Rect(1300,452,self.TileSize *1.5, self.TileSize *1.5)
        self.boots_rect = pygame.Rect(1536,746,self.TileSize *1.5 ,self.TileSize *1.5)
        # Paths
        self.path = "Graphics/Items"
        self.dir_list = os.listdir(self.path)
        # Image of items
        self.image = {"background": pygame.image.load('Graphics/Menu/Inventory/Inv.png').convert_alpha()}
        self.get_items()
        #Cursor
        self.cursor_image = pygame.transform.scale_by(pygame.image.load('Graphics/Menu Cursor.png').convert_alpha(),3)
        self.cursor = pygame.cursors.Cursor((15,5), self.cursor_image)
        #Last Selected
        self.last_selected_grid = None 
        self.last_selected_armour = None
        self.last_selected_weapon = None
        self.font = pygame.font.Font('Fonts/Montserrat-Bold.ttf', 50) # Font text
        self.page_no = 1 # Page no of the inv the player is on currently
        #Equipped slots
        self.armour_slot_used = {"Helmet": False,"Chest":False,"Gloves":False,"Boots":False}
        self.weapon_slot_used = {"Primary Weapon": False,"Secondary Weapon": False,"Ammo": False}
        #Stats of player
        self.melee_attack = 0
        self.ranged_attack = 0
        self.defence = 0
        self.health_added = 0
    
    def starter_kit(self):
        #Things equipped when starting a new save as a starter kit
        self.items.append(Item("Hard Leather Bow"))
        self.items.append(Item("Wood Arrow"))
        self.items.append(Item("Rusty Dagger"))
        for item in self.items:
            item.equipped = True
            if item.type["Primary Weapon"]:
                self.ranged_attack += item.attack
                self.weapon_slot_used["Primary Weapon"] = True
            if item.type["Secondary Weapon"]:
                self.melee_attack += item.attack
                self.weapon_slot_used["Secondary Weapon"] = True
            if item.type["Ammo"]:
                self.ranged_attack += item.attack
                self.weapon_slot_used["Ammo"] = True

        
        
        
        self.weapon_slot_used["Ammo"] = True
    
    def render_stat_selected(self):
        # Renders the stats of the currently selected item in the grid
        if self.last_selected_grid != None: # Checks if there is an item selected
            index = self.last_selected_grid # Gets the index of the grid selection
            if self.page_no != 1 and index != None : # Checks if the page no is not 1
                index += ((self.page_no-1) * 25) # Gets the index of the items
            # Checks if the index is less than the length of items
            if index < len(self.items):
                # Gets the item selected from the list of items
                item_selected = self.items[index]
                # Checks if the item is an attack type
                if item_selected.attack > 0:
                    # Checks if the item is a melee or ranged and displays how much ATK it will add
                    if item_selected.type["Secondary Weapon"]:
                        text = self.font.render(f'Melee: + {str(item_selected.attack)} ATK',True,"black")
                    if item_selected.type["Primary Weapon"] or item_selected.type["Ammo"]:
                        text = self.font.render(f'Ranged: + {str(item_selected.attack)} ATK',True,"black")
                # Checks if item is a piece of armour and displays how much DEF it will add
                if item_selected.defence > 0:
                    text = self.font.render(f'Defence: + {str(item_selected.defence)} DEF',True,"black")
                # Checks if item is a health consumable and displays how much health it will add
                if item_selected.health > 0:
                    text = self.font.render(f'Health: + {str(item_selected.health)} HP',True,"black")
                # Checks what the items rarity is and displays that to the player
                if item_selected.rarity != None:
                    rarity_text = self.font.render(f'rarity: {item_selected.rarity}', True,"black")
                    screen.blit(rarity_text,(840,200))
                
                screen.blit(text,(840,150))
                        
    def update_stats_player(self,upgrade):
        # Depending on the name of the upgrade the player can gain attack or defence
        if upgrade == "Ranged Attack":
            self.ranged_attack += 5
        if upgrade == "Melee Attack":
            self.melee_attack += 5
        if upgrade == "Defense":
            self.defence += 5
        
    def render_stats(self):
        # Renders the stats 
        melee_text = self.font.render(f'Melee: {str(self.melee_attack)} ATK',True,"black")
        range_text = self.font.render(f'Ranged: {str(self.ranged_attack)} ATK',True,"black")
        defence_text = self.font.render(f'Defence: {str(self.defence)} DEF',True,"black")
        screen.blit(melee_text,(840,350))
        screen.blit(range_text,(840,420))
        screen.blit(defence_text,(840,490))
    
    def render_name_currently_selected(self):
        if self.last_selected_grid != None: # Checks if a tile is selected
            index = self.last_selected_grid # Gets the index of the grid
            if self.page_no != 1 and index != None :
                index += ((self.page_no-1) * 25) # Gets the index for items
            # Checks if the index is less than the length of items
            if index < len(self.items):
                item_selected = self.items[index] # Gets the item from items
                # If the item is a consumable then the first 5 letters will need to be removed to just get the name of the item and to get rid of 'health'
                if item_selected.type["Health Consumable"]:
                    name = item_selected.name[5:]
                else:
                    name = item_selected.name
                # Gets the text of the name and renders it
                name_text = self.font.render(f'{name}',True,"black")
                screen.blit(name_text,(840,90))
    
    def render_equip_button(self):
        # Renders the equip text and the box
        text = self.font.render('Equip', True,"black")
        equipRect = text.get_rect(topleft =(892,580))
        # 1050 160
        self.equip_box_rect = pygame.Rect(840,580,self.TileSize*2,64)
        pygame.draw.rect(screen, "gray",self.equip_box_rect,border_radius= 20)
        screen.blit(text,equipRect)

    def check_consumable_selected(self):
        index = self.last_selected_grid # Gets the index of the grid
        if self.page_no != 1 and index != None :
            index += ((self.page_no-1) * 25) # Gets the index for items
        # Checks if the index is less than the length of items
        if index < len(self.items):
            item_selected = self.items[index] # Gets the item from items
            # Checks if it is a consumable and return true if it is or false if it isn't
            if item_selected.type["Health Consumable"]:
                return True
        return False
    
    def render_use_button(self):
        # Renders the use button
        text = self.font.render('Use', True,"black")
        UseRect = text.get_rect(topleft =(920,580))
        self.use_box_rect = pygame.Rect(840,580,self.TileSize*2,64)
        pygame.draw.rect(screen, "gray",self.use_box_rect,border_radius= 20)
        screen.blit(text,UseRect)
    
    def check_use_clicked(self):
        # Checks if the use button is clicked
        mx,my = pygame.mouse.get_pos()
        if self.use_box_rect.collidepoint(mx,my) and (pygame.mouse.get_pressed())[0] == True:
                self.use()
    
    def use(self):
        # Gets the index of the item
        index = self.last_selected_grid
        if self.page_no != 1 and index != None :
            index += ((self.page_no-1) * 25)
        if index < len(self.items):
            item_selected = self.items[index] # Gets the item from items
            self.items.remove(item_selected) # Removes the item from the inventory 
            self.health_added += item_selected.health # Items adds health to attribute health_added
        self.last_selected_grid = None
    
    def render_unequip_button(self):
        # Renders the unequip button
        text = self.font.render('Unequip', True,"black")
        unequipRect = text.get_rect(topleft =(858,580))
        self.unequip_box_rect = pygame.Rect(840,580,self.TileSize*2,64)
        pygame.draw.rect(screen, "gray",self.unequip_box_rect,border_radius= 20)
        
        screen.blit(text,unequipRect)
    
    def check_unequip_clicked(self):
        # Checks if the unequip button was clicked
        mx,my = pygame.mouse.get_pos()
        if self.unequip_box_rect.collidepoint(mx,my) and (pygame.mouse.get_pressed())[0] == True:
                self.unequip()
        
    def select_armour_slots(self):
        # Checks if the armour slots have been clicked or not
        mx,my = pygame.mouse.get_pos()
        if self.helmet_rect.collidepoint(mx,my) and (pygame.mouse.get_pressed())[0] == True:
            self.last_selected_grid = None
            self.last_selected_weapon = None
            self.last_selected_armour = self.helmet_rect
        if self.chest_rect.collidepoint(mx,my) and (pygame.mouse.get_pressed())[0] == True:
            self.last_selected_grid = None
            self.last_selected_weapon = None
            self.last_selected_armour = self.chest_rect
        if self.gloves_rect.collidepoint(mx,my) and (pygame.mouse.get_pressed())[0] == True:
            self.last_selected_grid = None
            self.last_selected_weapon = None
            self.last_selected_armour = self.gloves_rect
        if self.boots_rect.collidepoint(mx,my) and (pygame.mouse.get_pressed())[0] == True:
            self.last_selected_grid = None
            self.last_selected_weapon = None
            self.last_selected_armour = self.boots_rect
            
    def select_weapon_slots(self):
        # Checks if any of the weapon slots has been clicked
        mx,my = pygame.mouse.get_pos()
        if self.primary_rect.collidepoint(mx,my) and (pygame.mouse.get_pressed())[0] == True:
            self.last_selected_grid = None
            self.last_selected_armour = None
            self.last_selected_weapon = self.primary_rect
        if self.secondary_rect.collidepoint(mx,my) and (pygame.mouse.get_pressed())[0] == True:
            self.last_selected_grid = None
            self.last_selected_armour = None
            self.last_selected_weapon = self.secondary_rect
        if self.ammo_rect.collidepoint(mx,my) and (pygame.mouse.get_pressed())[0] == True:
            self.last_selected_grid = None
            self.last_selected_armour = None
            self.last_selected_weapon = self.ammo_rect
        
    def unequip(self):
        # Unequipes a selected item
        # Loops through all the items and checks which are equipped
        for item in self.items:
            if item.equipped == True:
                for type in item.type:
                    # Checks the item type
                    if item.type[type] == True:
                        # Checks what the last selected item was and if it matches the item type
                        # If it does it unequips the item and makes the slot free 
                        if type == "Helmet" and self.last_selected_armour == self.helmet_rect:
                            item.equipped = False
                            self.armour_slot_used[type] = False
                            self.defence -= item.defence
                        if type == "Chest" and self.last_selected_armour == self.chest_rect:
                            item.equipped = False
                            self.armour_slot_used[type] = False
                            self.defence -= item.defence
                        if type == "Gloves" and self.last_selected_armour == self.gloves_rect:
                            item.equipped = False
                            self.armour_slot_used[type] = False
                            self.defence -= item.defence
                        if type == "Boots" and self.last_selected_armour == self.boots_rect:
                            item.equipped = False
                            self.armour_slot_used[type] = False
                            self.defence -= item.defence
                        if type == "Primary Weapon" and self.last_selected_weapon == self.primary_rect:
                            item.equipped = False
                            self.weapon_slot_used[type] = False
                            self.ranged_attack -= item.attack
                        if type == "Secondary Weapon" and self.last_selected_weapon == self.secondary_rect:
                            item.equipped = False
                            self.weapon_slot_used[type] = False
                            self.melee_attack -= item.attack
                        if type == "Ammo" and self.last_selected_weapon == self.ammo_rect:
                            item.equipped = False
                            self.weapon_slot_used[type] = False
                            self.ranged_attack -= item.attack
                                                
    def check_equip_clicked(self):
        # Checks if equip button is clicked
        mx,my = pygame.mouse.get_pos()
        if self.equip_box_rect.collidepoint(mx,my) and (pygame.mouse.get_pressed())[0] == True:
            self.equip()
        
    def equip(self):
        # Equips item selected
        # Gets the index of the item
        index = self.last_selected_grid
        if self.page_no != 1 and index != None :
            index += ((self.page_no-1) * 25)
        if index < len(self.items):
            item_selected = self.items[index] # Gets the item from items
            # Checks if the item is already equipped or not
            if item_selected.equipped != True:
                for type in item_selected.type:
                    # Checks the type of item
                    if item_selected.type[type] == True:
                        # Checks if the type's slot is being used and increases either attack or defence
                        if type == "Helmet":
                            if self.armour_slot_used[type] == False:
                                item_selected.equipped = True
                                self.armour_slot_used[type] = True
                                self.defence += item_selected.defence
                        if type == "Chest":
                            if self.armour_slot_used[type] == False:
                                item_selected.equipped = True
                                self.armour_slot_used[type] = True
                                self.defence += item_selected.defence
                        if type == "Gloves":
                            if self.armour_slot_used[type] == False:
                                item_selected.equipped = True
                                self.armour_slot_used[type] = True
                                self.defence += item_selected.defence
                        if type == "Boots":
                            if self.armour_slot_used[type] == False:
                                item_selected.equipped = True
                                self.armour_slot_used[type] = True
                                self.defence += item_selected.defence
                        if type == "Primary Weapon":
                            if self.weapon_slot_used[type] == False:
                                item_selected.equipped = True
                                self.weapon_slot_used[type] = True
                                self.ranged_attack += item_selected.attack
                        if type == "Secondary Weapon":
                            if self.weapon_slot_used[type] == False:
                                item_selected.equipped = True
                                self.weapon_slot_used[type] = True
                                self.melee_attack += item_selected.attack
                        if type == "Ammo":
                            if self.weapon_slot_used[type] == False:
                                item_selected.equipped = True
                                self.weapon_slot_used[type] = True
                                self.ranged_attack += item_selected.attack
    
    def render_weapon_box(self):
        # Renders the weapons box (primary,secondary and ammo slots)
        self.secondary_rect = pygame.Rect(1300,810,self.TileSize,self.TileSize)
        self.primary_rect = pygame.Rect(1150,810,self.TileSize,self.TileSize)
        self.ammo_rect = pygame.Rect(1000,810,self.TileSize,self.TileSize)
        pygame.draw.rect(screen, "grey",self.primary_rect,border_radius= 20)
        pygame.draw.rect(screen, "grey",self.secondary_rect,border_radius= 20)
        pygame.draw.rect(screen,"grey",self.ammo_rect,border_radius = 20)
                  
    def render_primary_weapon(self,name):
        # Renders the primary weapon inside the slot
        screen.blit(pygame.transform.scale_by(self.image[name],1),(self.primary_rect.x,self.primary_rect.y))
    
    def render_secondary_weapon(self,name):
        # Renders the secondary weapon inside the slot
        screen.blit(pygame.transform.scale_by(self.image[name],1),(self.secondary_rect.x,self.secondary_rect.y))
                    
    def render_ammo_weapon(self,name):
        # Renders the ammo inside the slot
        screen.blit(pygame.transform.scale_by(self.image[name],1),(self.ammo_rect.x,self.ammo_rect.y))
    
    def render_equipped_items(self):
        # Renders all the items inside of their slots
        # Loops through each item
        for item in self.items:
            # Checks if the item is equipped
            if item.equipped == True:
                for type in item.type:
                    # Checks the item type
                    if item.type[type] == True:
                        # Depending on the type the item is rendered
                        if type == "Helmet":
                            self.render_helmet_item(item.name)
                        if type == "Chest":
                            self.render_chest_item(item.name)
                        if type == "Gloves":
                            self.render_gloves_item(item.name)
                        if type == "Boots":
                            self.render_boots_item(item.name)
                        if type == "Primary Weapon":
                            self.render_primary_weapon(item.name)
                        if type == "Secondary Weapon":
                            self.render_secondary_weapon(item.name)
                        if type == "Ammo":
                            self.render_ammo_weapon(item.name)
                                                        
    def render_helmet_item(self,name):
        # Renders helemet inside the slot
        screen.blit(pygame.transform.scale_by(self.image[name],1.5),(self.helmet_rect.x,self.helmet_rect.y))
    
    def render_chest_item(self,name):
        # Renders chestplate inside the slot
        screen.blit(pygame.transform.scale_by(self.image[name],2),(self.chest_rect.x + 4,(self.chest_rect.y)+40))
    
    def render_gloves_item(self,name):
        # Renders the gloves inside the slot
        screen.blit(pygame.transform.scale_by(self.image[name],1.5),(self.gloves_rect.x,self.gloves_rect.y))
    
    def render_boots_item(self,name):
        # Renders the boots inside the slot
        screen.blit(pygame.transform.scale_by(self.image[name],1.5),(self.boots_rect.x + 5,self.boots_rect.y))
        
    def render_grid(self):
        # Renders the grid tiles
        pos_y = 128 # Staring position y
        for y in range(self.max_grid_size):
            pos_x = 128 # Starting position x
            for x in range(self.max_grid_size):
                # Renders a gray square in the positions x and y and of the tilesize
                pygame.draw.rect(screen, "gray",pygame.Rect(pos_x,pos_y,self.TileSize,self.TileSize),border_radius= 30)
                # Appends the grid to the list
                self.grid_rects.append(pygame.Rect(pos_x,pos_y,self.TileSize,self.TileSize))
                pos_x += self.TileSize + 10 # Increments by 10 to create a 10 pixel gap along the x axis 
            pos_y += self.TileSize + 10 # Increments by 10 to create a 10 pixel gap along the y axis
                      
    def move_page_right(self):
        #Moves the pages right
        pages_required = len(self.items) // 25 # Checks the number of pages needed
        remainder = len(self.items) % 25 # Gets the remainder
        # If there is a remainder then the pages required increases by 1
        if remainder > 0:
                pages_required += 1
        page_no_corrected = self.page_no + 1 # Temporary variable that is stored to simulate the page no being +1
        # Checks to make sure the temporary variable is not greater than the pages required 
        if not(page_no_corrected > pages_required):
            self.page_no += 1
        
    def move_page_left(self):
        # Moves the page to the left
        if self.page_no != 1:
            self.page_no -= 1
   
    def render_armour(self):
        # Renders the armour inside the slots
        pygame.draw.rect(screen, "gray",self.helmet_rect,border_radius= 10)
        pygame.draw.rect(screen, "gray",self.chest_rect,border_radius= 10)
        pygame.draw.rect(screen,"gray",self.gloves_rect,border_radius = 10)
        pygame.draw.rect(screen, "gray",self.boots_rect,border_radius= 10)
        
    def render_merge_button(self):
        # Renders the merge button
        text = self.font.render('Sort', True,"black")
        sortRect = text.get_rect(topleft =(420,850))
        self.sort_box_rect = pygame.Rect(350,850,self.TileSize*2,64)
        pygame.draw.rect(screen, "gray",self.sort_box_rect,border_radius= 20)
        
        screen.blit(text,sortRect)
        
    def render_left_right_page(self):
        # Renders the buttons, left and right, that move the pages
        text = self.font.render('Right', True,"black")
        rightRect = text.get_rect(topleft =(685,850))
        self.right_box_rect = pygame.Rect(626,850,self.TileSize*2,64)
        pygame.draw.rect(screen, "gray",self.right_box_rect,border_radius= 20)
        screen.blit(text,rightRect)
        text = self.font.render('Left', True,"black")
        leftRect = text.get_rect(topleft =(144,850))
        self.left_box_rect = pygame.Rect(74,850,self.TileSize*2,64)
        pygame.draw.rect(screen, "gray",self.left_box_rect,border_radius= 20)
        screen.blit(text,leftRect)

    def render_currently_equipped_grid(self):
        # A purple box is rendered on the grid to represent an item being equipped
        currently_equipped_pos = []
        counter = 0 # Represents the grid position, starting from 0 (first tile)
        for i in range(((self.page_no-1) * 25),(self.page_no* 25)): # Loops from the starting item being displayed to the last item being displayed (loops 25 times)
            if i < len(self.items):
                item = self.items[i] # Gets the items from item
                if item.equipped:
                    # If the item is equipped then the counter is added to the list
                    currently_equipped_pos.append(counter)
            counter += 1
        # Checks the positions and gets the y and x of each grid tile and renders a purple tile 
        for pos in currently_equipped_pos:
            rect = self.grid_rects[pos]
            rect_x = rect.x
            rect_y = rect.y
            pygame.draw.rect(screen, "purple",pygame.Rect(rect_x,rect_y,self.TileSize ,self.TileSize ),border_radius= 30)
                                      
    def check_merge_clicked(self):
        # Checks if the sort button was clicked
        mx,my = pygame.mouse.get_pos()
        if self.sort_box_rect.collidepoint(mx,my) and (pygame.mouse.get_pressed())[0] == True:
            self.sort_inventory()
        
    def render_items(self):
        # Renders the items in the grid
        counter = (self.page_no-1) * 25 # Get the starting index of items 
        pos_y = 128 # Starting y position
        for y in range(self.max_grid_size):
            pos_x = 128 # Starting x position
            for x in range(self.max_grid_size):
                # Makes sure the counter is within range
                if counter < len(self.items):
                    item_name = self.items[counter].name # Gets the items name using counter
                    screen.blit(self.image[item_name],(pos_x,pos_y)) # Renders the item
                    pos_x += self.TileSize + 10 # Changes the x position by 10
                    counter += 1
                                
                            
            pos_y += self.TileSize + 10 # Changes the y position by 10
        
    def render(self):
        screen.fill("black")
        # Renders all possible inventory graphics
        screen.blit(self.image["background"],(0,0)) # Renders background
        if self.last_selected_grid != None: # Checks if anything has been selected
            self.render_selected()
            if not(self.check_consumable_selected()): # Checks if a consumable has been selected
                # Renders the equip buttons and checks for clicks
                self.render_equip_button()
                self.check_equip_clicked()
            else:
                # Renders the use buttons and checks for clicks
                self.render_use_button()
                self.check_use_clicked()
            # Renders the name and stats of item selected
            self.render_name_currently_selected()
            self.render_stat_selected()
        if self.last_selected_armour != None: # Checks if armour slots have been selected
            # Renders a selected box and the button and checks for clicks
            self.render_selected()
            self.render_unequip_button()
            self.check_unequip_clicked()
        if self.last_selected_weapon != None: # Checks if weapon slots have been selected
            # Renders a selected box and the button and checks for clicks
            self.render_selected()
            self.render_unequip_button()
            self.check_unequip_clicked()


        self.render_grid()
        self.render_currently_equipped_grid()
        self.render_weapon_box()
        self.render_armour()
        self.render_merge_button()
        self.render_items()
        self.render_left_right_page()
        self.render_equipped_items()
        self.render_stats()
                  
    def get_grid_index(self):
        # Gets the grid index
        mx,my = pygame.mouse.get_pos()
        for grid_rect in self.grid_rects:
            # Checks which grid the mouse collided with when it clicked
            if grid_rect.collidepoint(mx,my) and (pygame.mouse.get_pressed())[0] == True:
                # Makes only the grid be selected and returns the index of the grid tile selected
                self.last_selected_armour = None
                self.last_selected_weapon = None
                return(self.grid_rects.index(grid_rect))

    def selected(self):
        # Makes the last selected grid the clicked grid tile
        clicked_square = self.get_grid_index()
        # pos = clicked_square
        if clicked_square != None:
            self.last_selected_grid = (clicked_square)
        
    def render_selected(self):
        # Renders a yellow selected box on certain tiles/slots in the inventory to show the currently selected box
        if self.last_selected_grid != None: # Checks if a grid tile was selected
            index = self.last_selected_grid
            rect = self.grid_rects[index]
            # An offset of the current grid x and y position is added to show a yellow outline
            rect_x = rect.x - 10
            rect_y = rect.y - 10
            pygame.draw.rect(screen, "yellow",pygame.Rect(rect_x,rect_y,self.TileSize +20 ,self.TileSize + 20),border_radius= 30)
        if self.last_selected_armour != None: # Checks if an armour slot was selected
            rect = self.last_selected_armour
            # An offset of the current grid x and y position is added to show a yellow outline
            rect_x = rect.x - 5
            rect_y = rect.y - 5
            pygame.draw.rect(screen, "yellow",pygame.Rect(rect_x,rect_y,rect.width + 10 ,rect.height + 10),border_radius= 10)
        if self.last_selected_weapon != None: # Checks if a weapon slot was selected
            # An offset of the current grid x and y position is added to show a yellow outline
            rect = self.last_selected_weapon
            rect_x = rect.x - 5
            rect_y = rect.y - 5
            pygame.draw.rect(screen, "yellow",pygame.Rect(rect_x,rect_y,rect.width + 10 ,rect.height + 10),border_radius= 20)
                          
    def sort_inventory(self):
        # Runs the merge sort algorithm
        self.merge_sort(self.items)
                
    def merge_sort(self,arr):
        # Sorts the inventory in order of type and then in order of stats
        if len(arr) > 1: # Checks if the length of the array is greater than 1
            mid = len(arr) // 2 # Finds the middle of the array
            # Splits the array into left half and right half
            left_half = arr[:mid] 
            right_half = arr[mid:]
            # Recursion of the left and right half until they are single arrays
            self.merge_sort(left_half)
            self.merge_sort(right_half)
            # The merge then begins for each recursion 
            self.merge(arr, left_half, right_half)

    def merge(self, arr, left_half, right_half):
        # Defines the order of sorting with helmets being first then chest items,etc
        type_order = ["Helmet", "Chest", "Gloves", "Boots", "Ammo", "Primary Weapon", "Secondary Weapon", "Health Consumable"]
        i = 0 # i is for left half
        j = 0 # j is for the right half
        k = 0 # k is for the merged array
        
        # Merges the 2 halves based on the stats and type order
        while i < len(left_half) and j < len(right_half):
            left_item = left_half[i] # Gets the current item from left half
            right_item = right_half[j] # Gets the current item from right half

            # Gets the type indexes in the type order for the left and right items
            left_type_index = self.get_type_index(left_item, type_order)
            right_type_index = self.get_type_index(right_item, type_order)

            if left_type_index < right_type_index:  
                # If left item is of a type that comes first, keep it
                arr[k] = left_item
                i += 1 # Move the next item in left half
            elif left_type_index > right_type_index:
                # If right item is of a type that comes first, keep it
                arr[k] = right_item
                j += 1 # Move to the next item in the right half
            else:
                # If both items are of the same type, sort by attack/defence/health
                # Gets the stat for the left and right item either health,attack or defence
                left_stat = self.get_sorting_stat(left_item)
                right_stat = self.get_sorting_stat(right_item)

                if left_stat >= right_stat:  # Descending order
                    arr[k] = left_item
                    i += 1 # Move to the next item in the left half
                else:
                    arr[k] = right_item
                    j += 1 # Move to the next item in the right half

            k += 1 # Moves to the next position in the merged array

        # Ensures any remaining elements are added to array from the left and right half
        while i < len(left_half):
            arr[k] = left_half[i]
            i += 1
            k += 1

        while j < len(right_half):
            arr[k] = right_half[j]
            j += 1
            k += 1
    
    def get_sorting_stat(self, item):
        # Returns the stat of the inputted item
        if item.type["Health Consumable"]:
            return item.health
        elif item.type["Primary Weapon"] or item.type["Secondary Weapon"] or item.type["Ammo"]:
            return item.attack
        elif item.type["Helmet"] or item.type["Chest"] or item.type["Gloves"] or item.type["Boots"]:
            return item.defence
        return 0  # Default if no type is matched

    def get_type_index(self, item, type_order):
        index = 0
        for type_name in type_order:
            if item.type[type_name]:  # Check if this type is True
                return index
            index += 1
        return len(type_order)  # If no type is found, put item last

    
    def get_items(self):
        # Adds each item to get the name and path for image loading
        for file in self.dir_list: # Loops through the directory items
            path = self.path # Gets the path
            # Adds /file name to the path
            path+= "/" 
            path+=file
            # To get the name of the file the last 4 letters are removed which is the .png
            name = file[:-4]
            # The name is made to have titlecase (e.g. Rusty Sword)
            name = name.title()
            # Adds the image to the dictionary images
            if path != "Graphics/Items/.DS_Store": 
                self.image[name] = pygame.transform.scale_by(pygame.image.load(path).convert_alpha(),4)
    
    def main(self):
        # Sets the custom cursor
        pygame.mouse.set_cursor(self.cursor)
        while not(self.pause):
            # Pygame Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        # Checks if the left or right button was clicked
                        mx,my = pygame.mouse.get_pos()
                        if self.right_box_rect.collidepoint(mx,my):
                            self.move_page_right()
                        if self.left_box_rect.collidepoint(mx,my):
                            self.move_page_left()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.pause = True
            
            self.render()
            self.check_merge_clicked()
            self.selected()
            self.select_armour_slots()
            self.select_weapon_slots()
            
            pygame.display.update()
            clock.tick(60)

class Upgrade_Screen():
    def __init__(self,difficulty):
        self.pause = False
        self.background = pygame.image.load('Graphics/Menu/Upgrade Screen/background.png').convert_alpha()
        self.chosen_upgrade = None
        self.probabilities = self.get_start_probability(difficulty)
        self.start_time = 0
        self.type_upgrades = ["offensive","defensive","utility"]
        self.offensive_upgrades = ["Ranged Attack","Melee Attack","Projectile Speed","Fire Ability","Armor Penetration"]
        self.defensive_upgrades = ["Wind Ability","Max Health","Defense","Healing On Kill","Health Regeneration","Status Effect Duration Reduced"]
        self.utility_upgrades = ["Invisible Ability","Upgrade Wind","Upgrade Invisibility","Upgrade Fire","Cooldown Ability Reduced","Ammo Chance", "Movement Speed"]
        self.special_abilites = {"Fire": False,"Wind": False,"Invisible": False,"Healing On Kill":False,"Health Regeneration": False,"Ammo Chance":False}
        self.upgrade_1 = None
        self.upgrade_2 = None
        self.upgrade_3 = None
        self.font = pygame.font.Font('Fonts/Montserrat-Bold.ttf', 40)
        #Transformation Matrices after choosing a certain upgrade, 3x3
        # Column is offensive, defensive, utility
        # Rows are the probability contribution for offensive, defensive and utility
        # e.g. The first row shows how much each of the offensive, defensive and utility is distributed to the offensive probability
            # 0.3 of the offensive probability goes towards the offensive probability, 0.2 of the defensive probability goes towards the offensive probability and 0.5 of the utility probability goes towards the offensive probability
        self.offensive_chosen = [[0.3, 0.2, 0.5],
                                 [0.5, 0.3, 0.2], 
                                 [0.2, 0.5, 0.3]]

        self.defensive_chosen = [[0.4, 0.3, 0.5],  
                                 [0.4, 0.5, 0.2],  
                                 [0.2, 0.2, 0.3]] 

        self.utility_chosen = [[0.5, 0.3, 0.3],  
                               [0.3, 0.2, 0.5],  
                               [0.2, 0.5, 0.2]]  
    
    def get_start_probability(self,difficulty):
        # 3x1 Matrix for the probabilities
        # Starting probability is based on the difficulty chosen
        if difficulty == "Easy":
            return [[0.5],
                    [0.3],
                    [0.2]]
        if difficulty == "Medium":
            return [[0.4],
                    [0.35],
                    [0.25]]
        if difficulty == "Hard":
            return [[0.3],
                    [0.4],
                    [0.3]]
    
    def change_probability(self,chosen_type):
        # Changes the probability based on the upgrade chosen and applies dot product
        if chosen_type == "offensive":
            self.probabilities = self.dot_product(self.probabilities,self.offensive_chosen)
        if chosen_type == "defensive":
            self.probabilities = self.dot_product(self.probabilities,self.defensive_chosen)
        if chosen_type == "utility":
            self.probabilities = self.dot_product(self.probabilities,self.utility_chosen)
    
    def dot_product(self,matrixA,matrixB):
        # Applies dot product between 2 matrices
        # Gets the probabilities from matrix A
        offensive_probability = matrixA[0][0]
        defensive_probability = matrixA[1][0]
        utility_probability = matrixA[2][0]
        # For loop that goes through each probability(offensive, defensive and utility)
        for i in range(0,len(matrixA)):
            new_prob = 0 # Probability calculated based on the distribution of one of the current probabilities
            for multiplyer in range(0,3):
                # Gets each probability in the row and distributes to the new probability
                if multiplyer == 0:
                    # Gets a portion of the offensive probability
                    new_prob += (offensive_probability * matrixB[i][multiplyer])
                if multiplyer == 1:
                    # Gets a portion of the defensive probability
                    new_prob += (defensive_probability * matrixB[i][multiplyer])
                if multiplyer == 2:
                    # Gets a portion of the utility probability
                    new_prob += (utility_probability * matrixB[i][multiplyer])
            # Replaces the old probability with the new probability
            matrixA[i][0] = round(new_prob,2)
        return matrixA
    
    def valid_upgrade(self,upgrade):
        # Checks if the upgrade us valid
        valid = False
        special_ability = False
        words = upgrade.split() # Splits the name of the upgrade into words
        for word in words:
            # Checks if the word is any of the special abilities
            if word == "Fire":
                special_ability = True
                if self.special_abilites["Fire"] and upgrade != "Fire Ability": # Becomes valid if the player has unlocked the fire ability
                    valid = True
                elif not(self.special_abilites["Fire"]) and (upgrade == "Fire Ability" or upgrade == "Fire Reduced"): # Becomes valid if the player has not unlocked the fire ability and the upgrade is the ability or reduce time on fire
                    valid = True
            if word == "Wind":
                special_ability = True
                if self.special_abilites["Wind"] and upgrade != "Wind Ability": # Becomes valid if the player has unlocked the wind ability
                    valid = True
                elif not(self.special_abilites["Wind"]) and upgrade == "Wind Ability": # Becomes valid if the player has not unlocked the wind ability and the upgrade is the ability
                    valid = True
            if word == "Invisibility" or word == "Invisible": 
                special_ability = True
                if self.special_abilites["Invisible"] and upgrade != "Invisible Ability": # Becomes valid if the player has unlocked the invisible ability
                    valid = True
                elif not(self.special_abilites["Invisible"]) and upgrade == "Invisible Ability": # Becomes valid if the player has not unlocked the invisible ability and the upgrade is the ability
                    valid = True
        # Checks for other special abilities
        if upgrade == "Healing On Kill":
            special_ability = True
            if not(self.special_abilites["Healing On Kill"]):
                valid = True
        if upgrade == "Health Regeneration":
            special_ability = True
            if not(self.special_abilites["Health Regeneration"]):
                valid = True
        if upgrade == "Ammo Chance":
            if not(self.special_abilites["Ammo Chance"]):
                valid = True
        # If the upgrade was not a special ability then it is true
        if special_ability == False:
            valid = True
        return valid
                              
    def randomly_select_upgrade(self):
        # Randomly select an upgrade
        offensive_prob = self.probabilities[0][0]
        defensive_prob = self.probabilities[1][0]
        utility_prob = self.probabilities[2][0] 
        # Uses probabilities as weights to select a type of upgrade      
        type = (random.choices(self.type_upgrades,(offensive_prob,defensive_prob,utility_prob)))[0]
        # Depending on the type a random upgrade is selected
        if type == "offensive":
            upgrade = random.choices(self.offensive_upgrades)[0]
        if type == "defensive":
            upgrade = random.choices(self.defensive_upgrades)[0]
            # Different types of status effect reduces is randomly selected
            if upgrade == "Status Effect Duration Reduced":
                upgrade = random.choices(["Slowed Reduced","Webbed Reduced","Fire Reduced"])[0]
        if type == "utility":
            # Check in the player class of the abilities
            upgrade = random.choices(self.utility_upgrades)[0]
            # DIfferent types of ability cooldown reduces is randomly selected
            if upgrade == "Cooldown Ability Reduced":
                upgrade = random.choices(["Fire Cooldown","Wind Cooldown","Invisibility Cooldown"])[0]
        return upgrade

    def check_upgrade_selected_special(self):
        # Checks if the upgrade chosen was a special ability
        match self.chosen_upgrade:
            case "Fire Ability":
                self.special_abilites["Fire"] = True
            case "Wind Ability":
                self.special_abilites["Wind"] = True
            case "Invisible Ability":
                self.special_abilites["Invisible"] = True
            case "Healing On Kill":
                self.special_abilites["Healing On Kill"] = True
            case "Health Regeneration":
                self.special_abilites["Health Regeneration"] = True
            case "Ammo Chance":
                self.special_abilites["Ammo Chance"] = True
                
        
        
    def get_upgrade_render(self,upgrade):
        # Gets the image of the upgrade depending on the name
        match upgrade:
            case "Ranged Attack":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Ranged Boost.png")
            case "Melee Attack":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Melee Boost.png")
            case "Projectile Speed":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Projectile Speed.png")
            case "Fire Ability":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Fire Ability.png")
            case "Armor Penetration":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Armor Penetration.png")
            case "Wind Ability":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Wind Ability.png")
            case "Max Health":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Max Health.png")
            case "Defense":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Defense.png")
            case "Healing On Kill":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Healing On Kill.png")
            case "Health Regeneration":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Health Regeneration.png")
            case "Slowed Reduced":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Slowed Decrease.png")
            case "Webbed Reduced":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Webbed Decrease.png")
            case "Fire Reduced":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Fire Decrease.png")
            case "Invisible Ability":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Invisibility Ability.png")
            case "Upgrade Wind":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Wind Ability.png")
            case "Upgrade Invisibility":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Invisibility Ability.png")
            case "Upgrade Fire":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Fire Ability.png")
            case "Fire Cooldown":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Cooldown.png")
            case "Wind Cooldown":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Cooldown.png")
            case "Invisibility Cooldown":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Cooldown.png")
            case "Ammo Chance":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Ammo Chance.png")
            case "Movement Speed":
                return pygame.image.load("Graphics/Menu/Upgrade Screen/Upgrade Icons/Movement Speed.png")
    
    def get_upgrade_description(self,upgrade):
        # Gets the description of the upgrade based on the name
        match upgrade:
            case "Ranged Attack":
                return "+5 Ranged Damage"
            case "Melee Attack":
                return "+5 Melee Damage"
            case "Projectile Speed":
                return "+10% Projectile Speed"
            case "Fire Ability":
                return "Press F to Summon\na Fire Ring Around You\nThat Burns Enemies"
            case "Armor Penetration":
                return "Ignores 10% of \nEnemies' Defence"
            case "Wind Ability":
                return "Press E to Push Away\nEnemies Around You"
            case "Max Health":
                return "Increases Max Health\nby 10 HP"
            case "Defense":
                return "Increases Base\nDefence by 5"
            case "Healing On Kill":
                return "Killing an Enemy\nGives 5 HP"
            case "Health Regeneration":
                return "Regain Health Over\nTime 5 HP\nEvery 15 seconds"
            case "Slowed Reduced":
                return "Time Slowed is 10%\nShorter"
            case "Webbed Reduced":
                return "Time Webbed is 10%\nShorter"
            case "Fire Reduced":
                return "Time on Fire is 10%\nShorter"
            case "Invisible Ability":
                return "Press Q to\nBecome Invisible\nConfusing Enemies"
            case "Upgrade Wind":
                return "Wind Pushes Enemies\nFurther"
            case "Upgrade Invisibility":
                return "Invisibility Lasts 2 \nSeconds Longer"
            case "Upgrade Fire":
                return "Fire Does More\nDamage to Enemies"
            case "Fire Cooldown":
                return "Recharge Time of Fire\nReduced by 3 Seconds"
            case "Wind Cooldown":
                return "Recharge Time of Wind\nReduced by 3 Seconds"
            case "Invisibility Cooldown":
                return "Recharge Time of\nInvisibility is Reduced\nby 3 Seconds"
            case "Ammo Chance":
                return "20% Chance to Not\nUse Ammo"
            case "Movement Speed":
                return "Increases Movement\nSpeed by 5%"
        
    def render_first_upgrade(self):
        # Renders the first upgrade
        upgrade_image = self.get_upgrade_render(self.upgrade_1)
        upgrade_description = self.get_upgrade_description(self.upgrade_1)
        text_name = self.font.render(self.upgrade_1,True,"Purple")
        text_description = self.font.render(upgrade_description,True,"black")
        screen.blit(upgrade_image,(95,53))
        screen.blit(text_name,(80,600))
        screen.blit(text_description,(80,700))
    
    def render_second_upgrade(self):
        # Renders the second upgrade
        upgrade_image = self.get_upgrade_render(self.upgrade_2)
        upgrade_description = self.get_upgrade_description(self.upgrade_2)
        text_name = self.font.render(self.upgrade_2,True,"Purple")
        text_description = self.font.render(upgrade_description,True,"black")
        screen.blit(upgrade_image,(740,53))
        screen.blit(text_name,(725,600))
        screen.blit(text_description,(725,700))
        
    def render_third_upgrade(self):
        # Renders the third upgrade
        upgrade_image = self.get_upgrade_render(self.upgrade_3)
        upgrade_description = self.get_upgrade_description(self.upgrade_3)
        text_name = self.font.render(self.upgrade_3,True,"Purple")
        text_description = self.font.render(upgrade_description,True,"black")
        screen.blit(upgrade_image,(1380,53))
        screen.blit(text_name,(1365,600))
        screen.blit(text_description,(1365,700))
            
    def render(self):
        screen.fill("black")
        # Renders all elements on screen
        screen.blit(self.background,(0,0))
        self.render_first_upgrade()
        self.render_second_upgrade()
        self.render_third_upgrade()
    
    def main(self):
        # While loop runs if the there is no upgrade chosen
        while self.chosen_upgrade == None:
            # Pygame Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        current_time = pygame.time.get_ticks()
                        # Checks which upgrade was clicked
                        # Only allows clicks after 2 seconds to prevent accidental clicks
                        if (current_time - self.start_time) > 2000:
                            mx,my = pygame.mouse.get_pos()
                            if my > 17 and my < 983:
                                #Check First Upgrade Clicked
                                if mx > 27 and mx < 616:
                                    self.chosen_upgrade = self.upgrade_1
                                #Check Second Upgrade Clicked
                                if mx > 672 and mx < 1262:
                                    self.chosen_upgrade = self.upgrade_2
                                #Check Third Upgrade Clicked
                                if mx > 1314 and mx < 1905:
                                    self.chosen_upgrade = self.upgrade_3
            # Validates each upgrade and continues the while loop until all the upgrades are valid
            while self.upgrade_1 == None:
                self.upgrade_1 = self.randomly_select_upgrade()
                valid_1 = self.valid_upgrade(self.upgrade_1)
                self.upgrade_2 = self.randomly_select_upgrade()
                valid_2 = self.valid_upgrade(self.upgrade_2)
                self.upgrade_3 = self.randomly_select_upgrade()
                valid_3 = self.valid_upgrade(self.upgrade_3)
                if not(valid_1 and valid_2 and valid_3):
                    self.upgrade_1 = None
                    
            self.render()
            
            pygame.display.update()
            clock.tick(60)
        
        self.check_upgrade_selected_special()

class Save():
    def __init__(self,save_no):
        # Depending on the save no the database connection is made
        name_db = f'Game{save_no}.db'
        self.db = sqlite3.connect(name_db)
    
    def create_table_player(self):
        # Creates the player table
        cursor = self.db.cursor()
        # Checks if a table exists
        table_exist = cursor.execute("""SELECT name FROM sqlite_master WHERE type ='table' AND name = 'PLAYER'""").fetchall()
        if table_exist == []:
            table = """ CREATE TABLE PLAYER(
                        Difficulty TEXT,
                        MaxHealth INT,
                        Health INT,
                        PositionX INT,
                        PositionY INT,
                        Melee_atk INT,
                        Ranged_atk INT,
                        Defence INT,
                        Speed INT,
                        Level INT,
                        Experience INT,
                        Fire_ability INT,
                        Wind_ability INT,
                        Invisible INT,
                        Force_wind INT,
                        Wind_timer INT,
                        Enemy_burn_time INT,
                        Fire_timer INT,
                        Armor_penetration REAL,
                        Projectile_speed_increase REAL,
                        Ammo_chance INT,
                        Slowed_reduced  REAL,
                        Webbed_redued REAL,
                        Fire_reduced REAL,
                        Invisible_duration INT,
                        Invisible_timer INT,
                        Healing_kill INT,
                        Health_regeneration INT,
                        Room_y INT,
                        Room_x INT,
                        Respawns INT
                        )
                    """
            cursor.execute(table)
            cursor.close()
            self.db.commit()
        # Clears the table if it does exist already
        else:
            query = """DELETE FROM PLAYER"""
            cursor.execute(query)
            cursor.close()
            self.db.commit()
    
    def insert_table_player(self,player_obj,difficulty,room_pos):
        # Saved the player object and difficulty
        cursor = self.db.cursor()
        insert_query = """INSERT INTO PLAYER VALUES(
                            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
        cursor.execute(insert_query,(difficulty,player_obj.MaxHealth,player_obj.Health, player_obj.PlayerRect.x,player_obj.PlayerRect.y,player_obj.melee_atk,player_obj.ranged_atk,player_obj.Defence,player_obj.Speed,player_obj.Level,player_obj.Experience,player_obj.Abilities["Fire"],player_obj.Abilities["Wind"],player_obj.Abilities["Invisible"],player_obj.force_wind,player_obj.wind_timer,player_obj.enemy_burn_damage,player_obj.fire_timer,player_obj.armor_penetration,player_obj.projectile_speed_increase,player_obj.ammo_chance,player_obj.slowed_reduced,player_obj.webbed_reduced,player_obj.fire_reduced,player_obj.invisible_duration,player_obj.invisible_timer,player_obj.healing_kill,player_obj.health_regeneration,room_pos[0],room_pos[1],player_obj.respawns))
    
        cursor.close()
        self.db.commit()
       
    def create_table_level_layout(self):
        # Creates a table that represents the grid layout of the level
        cursor = self.db.cursor()
        table_exist = cursor.execute("""SELECT name FROM sqlite_master WHERE type ='table' AND name = 'LEVEL_LAYOUT'""").fetchall()
        if table_exist == []:
            table = """ CREATE TABLE LEVEL_LAYOUT(
                        Pos0 INT,
                        Pos1 INT,
                        Pos2 INT,
                        Pos3 INT,
                        Pos4 INT,
                        Pos5 INT,
                        Pos6 INT,
                        Pos7 INT,
                        Pos8 INT)"""
            cursor.execute(table)
            cursor.close()
            self.db.commit()
        # Clears the table if it does exist already
        else:
            query = """DELETE FROM LEVEL_LAYOUT"""
            cursor.execute(query)
            cursor.close()
            self.db.commit()
    
    def insert_level_layout(self,grid):
        # Inserts each row of the grid
        cursor = self.db.cursor()
        
        query = """INSERT INTO LEVEL_LAYOUT VALUES(
                        ?,?,?,?,?,?,?,?,?)"""
        for i in range(len(grid)):
            row = grid[i]
            cursor.execute(query,(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
                
        cursor.close()
        self.db.commit()
    
    def create_table_chests_checked(self):
        cursor = self.db.cursor()
        table_exist = cursor.execute("""SELECT name FROM sqlite_master WHERE type ='table' AND name = 'CHEST_EXPLORED'""").fetchall()
        if table_exist == []:
            table = """ CREATE TABLE CHEST_EXPLORED(
                        Pos_y INT,
                        Pos_x INT)"""
            cursor.execute(table)
            cursor.close()
            self.db.commit()
        else:
            query = """DELETE FROM CHEST_EXPLORED"""
            cursor.execute(query)
            cursor.close()
            self.db.commit()
    
    def insert_table_chests_checked(self,chest_explored):
        cursor = self.db.cursor()
        query = "INSERT INTO CHEST_EXPLORED VALUES(?,?)"
        for pos in chest_explored:
            cursor.execute(query,(pos[0],pos[1],))
            
    def create_table_enemies(self):
        # Creates a table to store each enemy
        cursor = self.db.cursor()
        table_exist = cursor.execute("""SELECT name FROM sqlite_master WHERE type ='table' AND name = 'ENEMIES'""").fetchall()
        if table_exist == []:
            table = """ CREATE TABLE ENEMIES(
                        RoomX INT,
                        RoomY INT,
                        Health INT,
                        MaxHealth INT,
                        Name TEXT,
                        PosX INT,
                        PosY INT,
                        Defence INT,
                        Speed INT,
                        State TEXT,
                        Strength INT,
                        ACD INT)"""
            cursor.execute(table)
            cursor.close()
            self.db.commit()
        # Clears the table if it does exist already
        else:
            query = """DELETE FROM ENEMIES"""
            cursor.execute(query)
            cursor.close()
            self.db.commit()
    
    def insert_enemies(self,enemy_rooms):
        # Inserts the enemy attributes
        cursor = self.db.cursor()
        query = """INSERT INTO ENEMIES VALUES(?,?,?,?,?,?,?,?,?,?,?,?)"""
        for room_pos in enemy_rooms:
            room_pos_x = room_pos[1]
            room_pos_y = room_pos[0]
            q = enemy_rooms[room_pos].queue
            for enemy in q:
                cursor.execute(query,(room_pos_x,room_pos_y,enemy.Health,enemy.MaxHealth,enemy.Name,enemy.EnemyRect.x,enemy.EnemyRect.y,enemy.Defence,enemy.Speed,enemy.state,enemy.Strength,enemy.attack_cool_down,))
        
        cursor.close()
        self.db.commit()

    def create_table_inventory_items(self):
        # Creates a table to store the items
        cursor = self.db.cursor()
        table_exist = cursor.execute("""SELECT name FROM sqlite_master WHERE type ='table' AND name = 'INV_ITEMS'""").fetchall()
        if table_exist == []:
            table = """ CREATE TABLE INV_ITEMS(
                        Name TEXT,
                        Equipped INT)"""
            cursor.execute(table)
            cursor.close()
            self.db.commit()
        # Clears the table if it does exist already
        else:
            query = """DELETE FROM INV_ITEMS"""
            cursor.execute(query)
            cursor.close()
            self.db.commit()
    
    def create_table_inventory_settings(self):
        # Stores settings for the inventory to be restored
        cursor = self.db.cursor()
        table_exist = cursor.execute("""SELECT name FROM sqlite_master WHERE type ='table' AND name = 'INV_SETTINGS'""").fetchall()
        if table_exist == []:
            table = """ CREATE TABLE INV_SETTINGS(
                        Helmet INT,
                        Chest INT,
                        Gloves INT,
                        Boots INT,
                        Primary_Weapon INT,
                        Secondary_Weapon INT,
                        Ammo INT,
                        Melee INT,
                        Ranged INT,
                        Defence INT)"""
            cursor.execute(table)
            cursor.close()
            self.db.commit()
        # Clears the table if it does exist already
        else:
            query = """DELETE FROM INV_SETTINGS"""
            cursor.execute(query)
            cursor.close()
            self.db.commit()
    
    def insert_table_inventory(self,inv_obj):
        # Inserts the inventory data
        cursor = self.db.cursor()
        items = inv_obj.items
        query = """INSERT INTO INV_ITEMS VALUES(?,?)"""
        for item in items:
            cursor.execute(query,(item.name,item.equipped))
        query = """INSERT INTO INV_SETTINGS VALUES(?,?,?,?,?,?,?,?,?,?)"""
        armour_slot_used = inv_obj.armour_slot_used
        weapon_slot_used = inv_obj.weapon_slot_used
        cursor.execute(query,(armour_slot_used["Helmet"],armour_slot_used["Chest"],armour_slot_used["Gloves"],armour_slot_used["Boots"],weapon_slot_used["Primary Weapon"],weapon_slot_used["Secondary Weapon"],weapon_slot_used["Ammo"],inv_obj.melee_attack,inv_obj.ranged_attack,inv_obj.defence))
        cursor.close()
        self.db.commit()
    
    def create_table_upgrade(self):
        # Creates the table for the upgrade screen
        cursor = self.db.cursor()
        table_exist = cursor.execute("""SELECT name FROM sqlite_master WHERE type ='table' AND name = 'UPGRADE_SCREEN'""").fetchall()
        if table_exist == []:
            table = """ CREATE TABLE UPGRADE_SCREEN(
                        Offensive_prob REAL,
                        Defensive_prob REAL,
                        Utility_prob REAL,
                        Fire INT,
                        Wind INT,
                        Invisible INT,
                        Healing_On_Kill INT,
                        Health_Regeneration INT,
                        Ammo_Chance INT)"""
            cursor.execute(table)
            cursor.close()
            self.db.commit()
        # Clears the table if it does exist already
        else:
            query = """DELETE FROM UPGRADE_SCREEN"""
            cursor.execute(query)
            cursor.close()
            self.db.commit()
    
    def insert_table_upgrade(self,upgrade_obj):
        # Inserts upgrade data into the table
        cursor = self.db.cursor()
        query = """INSERT INTO UPGRADE_SCREEN VALUES(?,?,?,?,?,?,?,?,?)"""
        probabilities = upgrade_obj.probabilities
        special_abilities = upgrade_obj.special_abilites
        cursor.execute(query,(probabilities[0][0],probabilities[1][0],probabilities[2][0],special_abilities["Fire"],special_abilities["Wind"],special_abilities["Invisible"],special_abilities["Healing On Kill"],special_abilities["Health Regeneration"],special_abilities["Ammo Chance"]))
        cursor.close()
        self.db.commit()
                    
    def save_game(self,player_obj,difficulty,level_layout,chest_positions,enemy_rooms,inv_obj,upgrade_obj,room_pos):
        # Creates the table or restores them and inserts the data into the tables to create a save file
        self.create_table_player()
        self.insert_table_player(player_obj,difficulty,room_pos)
        self.create_table_level_layout()
        self.insert_level_layout(level_layout)
        self.create_table_chests_checked()
        self.insert_table_chests_checked(chest_positions)
        self.create_table_enemies()
        self.insert_enemies(enemy_rooms)
        self.create_table_inventory_items()
        self.create_table_inventory_settings()
        self.insert_table_inventory(inv_obj)
        self.create_table_upgrade()
        self.insert_table_upgrade(upgrade_obj)
    
    def create_table_score(self):
        #Creates a table to store every score
        cursor = self.db.cursor()
        table_exist = cursor.execute("""SELECT name FROM sqlite_master WHERE type ='table' AND name = 'SCORES'""").fetchall()
        if table_exist == []:
            table = """ CREATE TABLE SCORES(
                        Score INT,
                        Difficulty TEXT)"""
            cursor.execute(table)
            cursor.close()
            self.db.commit()
    def insert_table_score(self,difficulty,score):
        #Inserts the score and difficulty
        cursor = self.db.cursor()
        query = """INSERT INTO SCORES VALUES(?,?)"""
        cursor.execute(query,(score,difficulty))
        cursor.close()
        self.db.commit()
        
class Load():
    def __init__(self,load_no):
        # Depending on the load no the database connection is made
        name_db = f'Game{load_no}.db'
        self.db = sqlite3.connect(name_db)
    
    def load_player(self):
        # Loads the player by selecting all fields and fetching them and loading them into the player object
        cursor = self.db.cursor()
        query = """SELECT * FROM PLAYER"""
        cursor.execute(query)
        self.db.commit()
        player_data = cursor.fetchall()[0]
        self.difficulty = player_data[0]
        MaxHealth = player_data[1]
        Health = player_data[2]
        Position_X = player_data[3]
        Position_Y = player_data[4]
        Melee_atk = player_data[5]
        Ranged_atk = player_data[6]
        Defence = player_data[7]
        Speed = player_data[8]
        Level = player_data[9]
        XP = player_data[10]
        if player_data[11] == 0:
            Fire_ability = False
        else:
            Fire_ability = True
        if player_data[12] == 0:
            Wind_ability = False
        else:
            Wind_ability = True
        if player_data[13] == 0:
            Invisible_ability = False
        else:
            Invisible_ability = True
        Force_wind = player_data[14]
        Wind_timer = player_data[15]
        Enemy_burn_time = player_data[16]
        Fire_timer = player_data[17]
        Armor_penetration = player_data[18]
        Projectile_speed_increase = player_data[19]
        if player_data[20] == 0:
            Ammo_chance = False
        else:
            Ammo_chance = True
        Slowed_reduced = player_data[21]
        Webbed_reduced = player_data[22]
        Fire_reduced = player_data[23]
        Invisible_duration = player_data[24]
        Invisible_timer = player_data[25]
        if player_data[26] == 0:
            Healing_kill = False
        else:
            Healing_kill = True
        if player_data[27] == 0:
            Health_regeneration = False
        else:
            Health_regeneration = True 
        self.room_y = player_data[28]
        self.room_x = player_data[29]      
        respawns = player_data[30]
        player = Player(MaxHealth,"Bob",Defence,Speed,Level,XP,(Position_X,Position_Y))
        player.Health = Health
        player.melee_atk = Melee_atk
        player.ranged_atk = Ranged_atk
        player.Abilities = {"Fire" : Fire_ability, "Wind": Wind_ability, "Invisible": Invisible_ability}
        player.force_wind = Force_wind
        player.wind_timer = Wind_timer
        player.enemy_burn_damage = Enemy_burn_time
        player.fire_timer = Fire_timer
        player.armor_penetration = Armor_penetration
        player.projectile_speed_increase = Projectile_speed_increase
        player.ammo_chance = Ammo_chance
        player.slowed_reduced = Slowed_reduced
        player.webbed_reduced = Webbed_reduced
        player.fire_reduced = Fire_reduced
        player.invisible_duration = Invisible_duration
        player.invisible_timer = Invisible_timer
        player.healing_kill = Healing_kill
        player.health_regeneration = Health_regeneration
        player.respawns = respawns
        cursor.close()
        return player
    
    def load_level_layout(self):
        # Loads the grid by selecting all fields and fetching them and recreates the grid
        cursor = self.db.cursor()
        query = """SELECT * FROM LEVEL_LAYOUT"""
        cursor.execute(query)
        self.db.commit()
        saved_grid = cursor.fetchall()
        blank_grid = [[],[],[],[],[]]
        # Gets each row and recreates the grid
        for i in range(len(saved_grid)):
            row = saved_grid[i]
            for number_row in row:
                blank_grid[i].append(number_row)
        final_grid = blank_grid
        return final_grid
    
    def load_chest_opened(self):
        #Loads in the rooms with chests that have been explored
        cursor = self.db.cursor()
        query = """SELECT * FROM CHEST_EXPLORED"""
        cursor.execute(query)
        self.db.commit()
        positions = cursor.fetchall()
        if positions != []:
            return positions
        
            
    def load_level_object(self):
        # Loads the player object and the gets all the necessary settings for the level 
        level_layout = self.load_level_layout()
        maximum_rooms = 0
        room_pos = []
        # Loop that gets the maximum rooms and room positions and the bos room position
        y = 0
        for row in level_layout:
            x = 0
            for tile in row:
                if tile != 0:
                    maximum_rooms += 1
                    room_pos.append([y,x])
                if tile == 3:
                    boss_room_pos = (y,x)
                x+=1
            y+=1
        # Recreates the level object and restores it
        Levels = Level(maximum_rooms,9,5,[2,4],self.difficulty)
        Levels.chest_opened_pos = self.load_chest_opened()
        print
        Levels.boss_room_pos = boss_room_pos
        Levels.grid = level_layout
        Levels.room_pos = room_pos
        Levels.dict_rooms_empty = Levels.array_to_dictionary()
        Levels.dir_rooms = Levels.find_rooms_around()
        return Levels
    
    def load_enemy_rooms(self,rooms_pos_empty):
        # Loads all the enemies and adds them to each room
        cursor = self.db.cursor()
        enemy_rooms = {}
        query = """SELECT * FROM ENEMIES WHERE RoomX = ? AND RoomY = ?"""
        # Goes through each room position and selects all the enemies that are in the room
        for pos in rooms_pos_empty:
            pos_x = pos[1]
            pos_y = pos[0]
            cursor.execute(query,(pos_x,pos_y))
            self.db.commit()
            enemies = cursor.fetchall()
            # Creates a queue object to store the enemies
            q = Queue(len(enemies))
            # Recreates the enemy object
            for enemy in enemies:
                Health = enemy[2]
                MaxHealth = enemy[3]
                Name = enemy[4]
                PosX = enemy[5]
                PosY = enemy[6]
                Defence = enemy[7]
                Speed = enemy[8]
                State = enemy[9]
                Strength = enemy[10]
                attack_cool_down = enemy[11]
                if Name == "Water" or Name == "Water Boss":
                    enemy_obj = Water_Monster(MaxHealth,Name,Strength,Defence,Speed,attack_cool_down,(PosX,PosY))
                elif Name == "Spider" or Name == "Spider Boss":
                    enemy_obj = Spider(MaxHealth,Name,Strength,Defence,Speed,attack_cool_down,(PosX,PosY))
                elif Name == "Fire" or Name == "Fire Boss":
                    enemy_obj = Fire_Monster(MaxHealth,Name,Strength,Defence,Speed,attack_cool_down,(PosX,PosY))
                else:
                    enemy_obj = Enemy(MaxHealth,Name,Strength,Defence,Speed,attack_cool_down,(PosX,PosY))
                enemy_obj.Health = Health
                enemy_obj.state = State
                # Adds the enemy to queue
                q.Enqueue(enemy_obj)
            # Adds the queue to the dicitonary enemy rooms with the key being the room position
            enemy_rooms[(pos_y,pos_x)] = q
        return enemy_rooms       
    
    def load_inventory(self):
        # Restores the inventory items and the settings
        cursor = self.db.cursor()
        inv = Inventory()
        items = []
        query = """SELECT * FROM INV_ITEMS"""
        cursor.execute(query)
        self.db.commit()
        items_table = cursor.fetchall()
        for item in items_table:
            name = item[0]
            if item[1] == 0:
                equipped = False
            else:
                equipped = True
            item_obj = Item(name)
            item_obj.equipped = equipped
            items.append(item_obj)
        inv.items = items
        query = """SELECT * FROM INV_SETTINGS"""
        cursor.execute(query)
        self.db.commit()
        settings = cursor.fetchall()[0]
        if settings[0] == 0:
            inv.armour_slot_used["Helmet"] = False
        else:
            inv.armour_slot_used["Helmet"] = True
        if settings[1] == 0:
            inv.armour_slot_used["Chest"] = False
        else:
            inv.armour_slot_used["Chest"] = True
        if settings[2] == 0:
            inv.armour_slot_used["Gloves"] = False
        else:
            inv.armour_slot_used["Gloves"] = True
        if settings[3] == 0:
            inv.armour_slot_used["Boots"] = False
        else:
            inv.armour_slot_used["Boots"] = True
        if settings[4] == 0:
            inv.weapon_slot_used["Primary Weapon"] = False
        else:
            inv.weapon_slot_used["Primary Weapon"] = True
        if settings[5] == 0:
            inv.weapon_slot_used["Secondary Weapon"] = False
        else:
            inv.weapon_slot_used["Secondary Weapon"] = True
        if settings[6] == 0:
            inv.weapon_slot_used["Ammo"] = False
        else:
            inv.weapon_slot_used["Ammo"] = True
        inv.melee_attack = settings[7]
        inv.ranged_attack = settings[8]
        inv.defence = settings[9]
        return inv
    
    def load_upgrade_screen(self):
        # Loads the upgrade screen
        cursor = self.db.cursor()
        query = """SELECT * FROM UPGRADE_SCREEN"""
        cursor.execute(query)
        self.db.commit()
        up_settings = cursor.fetchall()[0]
        up_obj = Upgrade_Screen(self.difficulty)        
        probabilities = [[up_settings[0]],[up_settings[1]],[up_settings[2]]]
        special_abilites = {"Fire": up_settings[3],"Wind": up_settings[4],"Invisible": up_settings[5],"Healing On Kill":up_settings[6],"Health Regeneration": up_settings[7],"Ammo Chance":up_settings[8]}
        up_obj.probabilities = probabilities
        up_obj.special_abilites = special_abilites
        return up_obj
    
    def load_score_difficulty(self):
        # Gets the average difficulty
        difficulty_score_average = {"Easy":0,"Medium":0,"Hard":0}
        cursor = self.db.cursor()
        table_exist = cursor.execute("""SELECT name FROM sqlite_master WHERE type ='table' AND name = 'SCORES'""").fetchall()
        if table_exist != []:
            query = """ SELECT AVG(Score) FROM SCORES WHERE Difficulty = ? """
            for difficulty in difficulty_score_average:
                cursor.execute(query,(difficulty,))
                dif_average = cursor.fetchall()[0]
                if (dif_average[0]) != None:
                    difficulty_score_average[difficulty] = dif_average[0]
        return difficulty_score_average

class Stack():
    def __init__(self):
        #Front of array is bottom of stack
        self.stack = [None] * 100
        self.top = 0

    def check_empty(self):
        # Checks if the stack is empty
        if self.stack[0] == None:
            return True
        else:
            return False
    
    def peek(self):
        # Gets the top item of the stack
        return self.stack[self.top-1]
    
    def push(self,value):
        # Adds a value to the top of the stack
        self.stack[self.top] = value
        self.top += 1
    
    def pop(self):
        # Removes the top item from the stack
        if not(self.check_empty()):
            value = self.stack[self.top-1]
            self.stack[self.top-1] = None
            self.top -= 1
            return value
        
class Game:
    def __init__(self):
        self.menus_screen = Menu()
        self.menus_screen.main_menu()
        difficulty = self.menus_screen.difficulty_chosen
        saved_selected = self.menus_screen.select_saves
        # Checks if a save has been selected
        if difficulty == None:
            # Loads the game attributes
            for save in saved_selected:
                if saved_selected[save]:
                    if save == "Save 1":
                        l = Load(1)
                    if save == "Save 2":
                        l = Load(2)
                    if save == "Save 3":
                        l = Load(3)
            self.player = l.load_player()
            self.difficulty = l.difficulty
            self.no_rooms = self.get_no_rooms()
            self.Levels = l.load_level_object()
            self.enemy_rooms = l.load_enemy_rooms(self.Levels.room_pos)
            self.inv = l.load_inventory()
            self.up_screen = l.load_upgrade_screen()
            self.current_y = l.room_y # Used to get the row of the grid
            self.current_x = l.room_x # Used to get the tile of the grid 
        # Otherwise its a new game with default setting and random rooms
        else:
            self.player = Player(200,"Bob",5,5,0,0,(800,140))
            self.difficulty = difficulty
            self.no_rooms = self.get_no_rooms()
            self.Levels = Level(self.no_rooms, 9, 5,[2,4],self.difficulty)
            self.enemy_names = ["Skeleton","Ghost","Spider","Fire","Water"]
            self.enemy_rooms = self.assign_enemies_room(self.Levels.dict_rooms_empty,self.no_rooms,10)
            self.inv = Inventory()
            self.inv.starter_kit()
            self.up_screen = Upgrade_Screen(self.difficulty)
            self.current_y = 2 # Used to get the row of the grid
            self.current_x = 4 # Used to get the tile of the grid 
        self.invincible_time = 3000 #Time the player is invincible
        #Reload attributes
        self.reload_timer =  1000 #Time the player needs to reload
        self.need_reload_time = 0
        self.reload = False
        
        self.get_drop_rates()
        self.running = True
        self.Levels_layout = self.Levels.grid # Level grid layout
        self.clicked = False
        self.current_q = self.enemy_rooms[(self.current_y,self.current_x)] # Current room enemy queue
        # Cursor settings
        self.cursor_image = pygame.transform.scale_by(pygame.image.load('Graphics/Weapon Cursor.png').convert_alpha(), 2.5)
        self.cursor = pygame.cursors.Cursor((10,5),self.cursor_image)
        # Menues is a stack
        self.menus = Stack()
        self.menus.push("Game")
        self.current_state = self.menus.peek()
        # Showing the area of effect
        self.show_radius = {"Melee": False, "Fire": False}
        self.same_room = False
        self.chest_tile = False
    
    def Main(self):
        self.reset_enemy_start()
        self.player.player_reset()
        while self.running:
            # Pygame Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    # Reloads the players ammo
                    if event.key == pygame.K_r:
                        if self.player.Ammo < 10:
                            if self.reload == False:
                                self.reload = True
                                self.need_reload_time = pygame.time.get_ticks()
                    # Activates the fire ability
                    if event.key == pygame.K_f and self.player.Abilities["Fire"]:
                        current_time = pygame.time.get_ticks()
                        if (current_time - self.player.last_fire_used) >= self.player.fire_timer:
                            self.current_q.queue = self.player.fire_ability(self.current_q)
                            self.player.last_fire_used = current_time
                    # Activates the wind ability
                    if event.key == pygame.K_e and self.player.Abilities["Wind"]:
                        current_time = pygame.time.get_ticks()
                        if (current_time - self.player.last_wind_used) >= self.player.wind_timer:
                            self.current_q.queue = self.player.wind_ability(self.current_q)
                            self.player.last_wind_used = current_time
                    # Activates the invisible ability
                    if event.key == pygame.K_q and self.player.Abilities["Invisible"]:
                        current_time = pygame.time.get_ticks()
                        if (current_time - self.player.last_invisible_used) >= self.player.invisible_timer:
                            self.player.Status_Effects["Invisible"] = True
                            self.player.last_invisible_used = current_time
                    # Makes the current state the pause screen
                    if event.key == pygame.K_ESCAPE:
                        if self.current_state == "Game":
                            temp = self.menus.pop()
                            self.menus.push("Pause Screen")
                    # Opens the inventory screen and changes state        
                    if event.key == pygame.K_i:
                        temp = self.menus.pop()
                        self.menus.push("Inv")
                        self.inv.pause = False
                        
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.current_state == "Game":
                        # Shoots a bullet
                        if event.button == 1:
                            self.player.shoot_bullet()
                            self.check_chest_clicked()
                        # Melee attack activates
                        if event.button == 3:
                            self.MeleeAttack()
                            self.show_radius["Melee"] = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.current_state == "Game":
                        # Deactivates the melee radius from being shown
                        if event.button == 3:
                            self.show_radius["Melee"] = False
                            
                
            if self.current_state == "Game":
                self.current_state = self.menus.peek() # Checks the current state
                # Applies the custom cursor
                pygame.mouse.set_cursor(self.cursor)
                self.player.apply_status_effects()
                # Gets the current level components
                current_level_tiles, door_tiles,current_level_array = self.get_level_components()
                self.check_status_effect()
                # Renders the radius of melee or fire
                if self.show_radius["Melee"]:
                    pygame.draw.circle(screen, "grey", (self.player.PlayerRect.centerx,self.player.PlayerRect.centery),96)
                if self.show_radius["Fire"]:
                    pygame.draw.circle(screen, "red", (self.player.PlayerRect.centerx,self.player.PlayerRect.centery),192)
                self.show_radius_fire()
                self.render(current_level_tiles,current_level_array,door_tiles)
                self.check_collisions(door_tiles,current_level_tiles)
                self.Levels.determine_door_direction((self.current_y,self.current_x))
                self.enemies_attack()
                self.player.check_if_invincible(self.invincible_time)
                self.update_players_stats()
                self.give_health_item()
                self.check_if_win()
                if self.player.Die():
                    temp = self.menus.pop()
                    self.menus.push("Death")
            # Checks for other states
            if self.current_state != "Game":
                self.current_state = self.menus.peek() # Checks the current state
                # Inventory Screen
                if self.current_state == "Inv":
                    self.inv.main()
                    self.add_health()
                    temp = self.menus.pop()
                    self.menus.push("Game")
                    self.show_radius["Melee"] = False
                # Upgrade Screen
                if self.current_state == "Upgrade":
                    self.up_screen.start_time = pygame.time.get_ticks()
                    self.up_screen.main()
                    upgrade = self.up_screen.chosen_upgrade
                    self.up_screen.chosen_upgrade = None
                    self.up_screen.upgrade_1 = None
                    self.player.apply_upgrade(upgrade)
                    self.inv.update_stats_player(upgrade)
                    temp = self.menus.pop()
                    self.show_radius["Melee"] = False
                    self.menus.push("Game")
                # Pause Screen
                if self.current_state == "Pause Screen":
                    selected = self.menus_screen.pause_screen()
                    temp = self.menus.pop()
                    if selected["Play"]:
                        self.menus.push("Game")
                    if selected["Save"]:
                        self.menus.push("Save")
                    if selected["Exit"]:
                        temp = self.menus.pop()
                        self.menus.push("Main")
                    self.show_radius["Melee"] = False
                # Save Screen
                if self.current_state == "Save":
                    save_slot = self.menus_screen.save_screen()
                    save = None
                    temp = self.menus.pop()
                    if save_slot["Save 1"]:
                        save = Save(1)
                    if save_slot["Save 2"]:
                        save = Save(2)
                    if save_slot["Save 3"]:
                        save = Save(3)
                    if save != None:
                        save.save_game(self.player,self.difficulty,self.Levels_layout,self.Levels.chest_opened_pos,self.enemy_rooms,self.inv,self.up_screen,(self.current_y,self.current_x))
                    self.show_radius["Melee"] = False
                    self.menus.push("Game")
                self.reset_enemy_start()
                # Death Screen
                if self.current_state == "Death":
                    selected = self.menus_screen.death_screen()
                    temp = self.menus.pop()
                    if selected["Respawn"]:
                        self.player.respawns += 1
                        self.player.player_reset()
                        self.reset_enemy_start()
                        self.player.Health = self.player.MaxHealth
                        self.show_radius["Melee"] = False
                        self.menus.push("Game")
                    if selected["Save"]:
                        self.menus.push("Save")
                    if selected["Exit"]:
                        self.menus.push("Main")
                if self.current_state == "Win":
                    no_rooms_score = (self.check_rooms_cleared()) * 1000
                    score = no_rooms_score - (self.player.respawns * 100)
                    if score < 100:
                        score = 100
                    save = Save("Score")
                    save.create_table_score()
                    save.insert_table_score(self.difficulty,score)
                    self.menus_screen.win_screen(score)
                    self.menus.push("Main")
                # Sent back to the main menu
                if self.current_state == "Main":
                    self.running = False
                
            
            pygame.display.update()
            clock.tick(60)
        self.running = True
    
    def check_reload(self):
        # Checks if the player is able to reload
        if self.reload:
            current_time = pygame.time.get_ticks()
            if (current_time - self.need_reload_time) >= self.reload_timer:
                self.reload = False
                self.player.Ammo = 10
        
    def get_no_rooms(self):
        # returns the number of rooms the dungeon has for different difficulty level
        if self.difficulty == "Easy":
            return 5
        if self.difficulty == "Medium":
            return 10
        if self.difficulty == "Hard":
            return 15

    def check_chest_clicked(self):
        # Checks if the chest has been clicked on and gives an epic item
        if self.Levels_layout[self.current_y][self.current_x] == 2: # Checks if the room is a treasure room
            mx,my = pygame.mouse.get_pos()
            v = False
            # Checks if the room is has a chest that has been opened
            for pos in self.Levels.chest_opened_pos:
                if pos == (self.current_y,self.current_x):
                    v = True
            # Checks if the the chest is closed and all enemies has been cleared
            if self.Levels.chest == self.Levels.chest_closed and self.check_all_enemies_cleared_room(self.current_q.queue):
                if self.chest_tile.collidepoint(mx,my) and not(v): # Makes sure the mouse has clicked the chest and it has not been opened
                    correct_rarity = False
                    items = self.inv.image
                    #Makes sure an epic item is selected
                    while not(correct_rarity):
                        random_number = random.randint(1,(len(items)-1))
                        counter = 1
                        for item in items:
                            if item != "background":
                                if counter == random_number:
                                    selected_item = Item(item)
                                    if selected_item.rarity == "Epic":
                                        correct_rarity = True
                            counter += 1
                    if correct_rarity:
                        #Makes the chest now open and stores it in the array
                        self.Levels.chest = self.Levels.chest_open
                        self.Levels.chest_opened_pos.append((self.current_y,self.current_x))
                        self.inv.items.append(selected_item)
            if v:
                self.Levels.chest = self.Levels.chest_open
            

        
    def render_ui(self):
        #Renders the UI at the bottom of the screen
        font = pygame.font.Font('Fonts/Montserrat-Bold.ttf', 50) # Font text
        # Rooms left to clear
        no_rooms_to_clear = self.no_rooms - self.check_rooms_cleared() 
        rooms_left_text = font.render(f'ROOMS LEFT: {no_rooms_to_clear}',True,"White") 
        # Player level
        player_level_text = font.render(f'LEVEL: {self.player.Level}',True,"White")
        # Status Effects
        staus_effects_active = self.player.Status_Effects
        if staus_effects_active["Webbed"]:
            webbed = pygame.transform.scale_by(pygame.image.load('Graphics/UI/Webbed.png').convert_alpha(),0.5)
            screen.blit(webbed,(1790,90))
        if staus_effects_active["Burning"]:
            burning = pygame.image.load('Graphics/UI/On Fire.png').convert_alpha()
            screen.blit(burning,(1800,350))
        if staus_effects_active["Slowed"]:
            slowed = pygame.transform.scale_by(pygame.image.load('Graphics/UI/Slowed.png').convert_alpha(),0.7)
            screen.blit(slowed,(1790,220))
        # Player Abilities
        abilities_gained = self.player.Abilities
        if abilities_gained["Fire"]:
            fire = pygame.transform.scale_by(pygame.image.load('Graphics/UI/Fire Ability.png').convert_alpha(),0.3)
            current_time = pygame.time.get_ticks()
            time_left = ((self.player.fire_timer-(current_time - self.player.last_fire_used))//1000) + 1
            key = font.render("F",True,"White")
            screen.blit(key,(940,1100))
            if time_left > 0:
                time_left_text = font.render(f'{time_left}',True,"White")
                fire.set_alpha(100)
                screen.blit(fire,(900,950))
                screen.blit(time_left_text,(940,1000))
            else:
                fire.set_alpha(255)
                screen.blit(fire,(900,950))
        if abilities_gained["Wind"]:
            wind = pygame.transform.scale_by(pygame.image.load('Graphics/UI/Wind.png').convert_alpha(),0.3)
            current_time = pygame.time.get_ticks()
            time_left = ((self.player.wind_timer-(current_time - self.player.last_wind_used))//1000) + 1
            key = font.render("E",True,"White")
            screen.blit(key,(670,1100))
            if time_left > 0:
                time_left_text = font.render(f'{time_left}',True,"White")
                wind.set_alpha(100)
                screen.blit(wind,(630,950))
                screen.blit(time_left_text,(670,1000))
            else:
                wind.set_alpha(255)
                screen.blit(wind,(630,950))
        if abilities_gained["Invisible"]:
            invisible = pygame.transform.scale_by(pygame.image.load('Graphics/UI/Invisibility Ability.png').convert_alpha(),0.3)
            current_time = pygame.time.get_ticks()
            time_left = ((self.player.invisible_timer-(current_time - self.player.last_invisible_used))//1000) + 1
            key = font.render("Q",True,"White")
            screen.blit(key,(1210,1100))
            if time_left > 0:
                time_left_text = font.render(f'{time_left}',True,"White")
                invisible.set_alpha(100)
                screen.blit(invisible,(1170,950))
                screen.blit(time_left_text,(1210,1000))
            else:
                invisible.set_alpha(255)
                screen.blit(invisible,(1170,950))
                
        # Ammo Number Render
        bullet_surface = pygame.transform.scale_by(pygame.image.load('Graphics/Bullet/BulletA1.png').convert_alpha(),6)
        ammo_text = font.render(f'{self.player.Ammo}',True,"White")
        # Render
        screen.blit(bullet_surface,(1850,10))
        screen.blit(ammo_text,(1790,10))
        screen.blit(player_level_text,(0,1000))
        self.player.render_player_bars()
        screen.blit(rooms_left_text,(1400,1000))
        
    def check_if_win(self):
        # Checks if the player wins by checking if all enemies in the boss room has been cleared
        enemies_list_boss = self.enemy_rooms[self.Levels.boss_room_pos].queue
        win = self.check_all_enemies_cleared_room(enemies_list_boss)
        if win:
            temp = self.menus.pop()
            self.menus.push("Win")
    
    def check_rooms_cleared(self):
        # Checks the number of rooms that have been cleared
        no_rooms_cleared = 0
        for pos in self.Levels.room_pos:
            pos_y = pos[0]
            pos_x = pos[1]
            enemies_list = self.enemy_rooms[(pos_y,pos_x)].queue
            if self.check_all_enemies_cleared_room(enemies_list):
                no_rooms_cleared += 1
        return no_rooms_cleared
    
    def random_xp(self):
        # Returns a random number of XP depending on the difficulty
        if self.difficulty == "Easy":
            return random.randint(10,20)
        if self.difficulty == "Medium":
            return random.randint(7,15)
        if self.difficulty == "Hard":
            return random.randint(5,10)
    
    def check_all_enemies_cleared_room(self,enemy_list):
        # Checks if the current room is cleared
        Enemies = enemy_list
        for enemy in Enemies:
            if enemy.state == "active":
                return False
        return True
    
    def give_health_item(self):
        # Gives a health consumable item every time the player clears the room
        cleared = self.check_all_enemies_cleared_room(self.current_q.queue)
        if cleared and not(self.same_room):
            item_type = "Health Consumable"
            correct_type = False
            items = self.inv.image
            while not(correct_type):
                random_number = random.randint(1,(len(items)-1))
                counter = 1
                for item in items:
                    if item != "background":
                        if counter == random_number:
                            selected_item = Item(item)
                            if selected_item.type[item_type]:
                                correct_type = True
                    counter += 1
            if correct_type:
                self.inv.items.append(selected_item)
            self.same_room = True
    
    def get_drop_rates(self):
        # Gets the probabilites of each rarity depending on
        self.rarities = {"Common" : 1, "Uncommon": 2, "Rare": 3, "Epic": 4}
        # Get rarity probability
        if self.difficulty == "Easy":
            x = 1.2
        if self.difficulty == "Medium":
            x = 1.5
        if self.difficulty == "Hard":
            x = 2
        for rarity in self.rarities:
            rarity_level = self.rarities[rarity]
            # Exponential function to get the rarity
            self.rarities[rarity] = round((1 / (rarity_level ** x)),4)
        # Normalising Drop Rates so they add up to 1
        total = 0
        # Sums up all the probabilities 
        for rarity in self.rarities:
            probability = self.rarities[rarity]
            total += probability
        for rarity in self.rarities:
            probability = self.rarities[rarity]
            self.rarities[rarity] = round(probability/total, 2)
        
    def add_health(self):
        # Adds health to the player the user has consumed from the inventory
        self.player.Health += self.inv.health_added
        self.inv.health_added = 0
    
    def show_radius_fire(self):
        # Makes sure the radius is displayed for 2 seconds
        current_time = pygame.time.get_ticks()
        if (current_time - self.player.last_fire_used) <= 200:
            self.show_radius["Fire"] = True
        else:
            self.show_radius["Fire"] = False
            
    def check_status_effect(self):
        # Checks status effects of each enemy and applies them
        Enemies = self.current_q.queue
        for enemy in Enemies:
            enemy.apply_burning_effect()
            enemy.check_still_burning()
            enemy.move_wind()
    
    def reset_enemy_start(self):
        # Resets each enemy in the room
        Enemies = self.current_q.queue
        for enemy in Enemies:
            enemy.reset_start()
    
    def get_level_components(self):
        # Gets each level components
        if self.Levels_layout[self.current_y][self.current_x] == 1:
            current_level_tiles,door_tiles = self.Levels.basic_room_render()
            current_level_array = self.Levels.basic_room
        if self.Levels_layout[self.current_y][self.current_x] == 2:
            current_level_tiles,door_tiles,self.chest_tile = self.Levels.treasure_room_render()
            current_level_array = self.Levels.treasure_room
        if self.Levels_layout[self.current_y][self.current_x] == 3:
            current_level_tiles,door_tiles = self.Levels.boss_room_render()
            current_level_array = self.Levels.boss_room
        return current_level_tiles,door_tiles,current_level_array
    
    def check_collisions(self,door_tiles,current_level_tiles):
        # Checks all collisions
        self.check_collision_door(door_tiles)
        self.check_collision_bullet_player(current_level_tiles)
        self.check_collision_bullet_enemy(current_level_tiles)
       
    def render(self,current_level_tiles,current_level_array,door_tiles):
        # Renders all elements of the game
        self.player.render(current_level_tiles)
        self.render_ui()
        self.render_enemies(current_level_array,current_level_tiles,door_tiles)
        self.render_bullets()
    
    def check_enemies_dead(self):
        # Checks if the enemies dies
        Enemies = self.current_q.queue
        for enemy in Enemies:
            if enemy.state == "active":
                enemy_delete = enemy.Die()
                if enemy_delete:
                    # If the player has the abilit to gain health on kill
                    if self.player.healing_kill:
                        self.player.Health += 5
                    random_drop_enemy = enemy.drop_randomly(self.inv.image,self.rarities)
                    self.inv.items.append(random_drop_enemy)
                    enemy.state = "unactive"

                    self.player.GainXP(self.random_xp())
                    level_up = self.player.LevelUp()
                    if level_up:
                        temp = self.menus.pop()
                        self.menus.push("Upgrade")
    
    def MeleeAttack(self):
        # Applies damage to enemies close by
        radius = 128
        Enemies = self.current_q.queue
        for enemy in Enemies:
            # Checks if enemy is are within a radius 
            if enemy.state == "active":
                #Pythagoras' theorem
                distance = math.sqrt((enemy.EnemyRect.x - self.player.PlayerRect.x)** 2 + (enemy.EnemyRect.y - self.player.PlayerRect.y) ** 2)
                if distance <= radius:
                    damage = enemy.TakeDamage(self.player.melee_atk,self.player.armor_penetration)
                    enemy.Health -= damage
        self.check_enemies_dead()
                   
    def update_players_stats(self):
        # Updates the state of the player
        self.player.melee_atk = self.inv.melee_attack
        self.player.ranged_atk = self.inv.ranged_attack
        self.player.Defence = self.inv.defence
        if self.player.Ammo == 0:
            if self.reload != True:
                self.need_reload_time = pygame.time.get_ticks()
                self.reload = True
        self.check_reload()
        if self.player.health_regeneration:
            self.player.regeneration()
        self.player.check_health_correct()
        
    def render_enemy_bars(self):
        # Renders the enemies health bars
        Enemies = self.current_q.queue
        for enemy in Enemies:
            if enemy != None:
                if enemy.state == "active":
                    enemy.health_bar.render(screen,enemy.Health,enemy.EnemyRect.x,enemy.EnemyRect.y)
    
    def render_bullets(self):
        # Renders the player bullets
        for b in self.player.projectiles:
                b.move_bullet()
                screen.blit(b.Bullet,b.Bullet_Rect)
        # Renders the enemeies' bullets
        Enemies = self.current_q.queue
        for enemy in Enemies:
            if enemy != None:
                for b in enemy.projectiles:
                    b.move_bullet()
                    screen.blit(b.Bullet,b.Bullet_Rect)
    
    def render_enemies(self,current_level_array,current_level_tiles,current_door_tiles):
        # Renders the enemies
        Enemies = self.current_q.queue
        for enemy in Enemies:
            if enemy != None:
                if enemy.state == "active":
                    enemy.render()
                    enemy.can_start()
                    if not(enemy.wind[0]) and not(self.player.Status_Effects["Invisible"]):
                        if (enemy.Name == "Spider" or enemy.Name == "Spider Boss") and self.player.Status_Effects["Webbed"] == True:
                            enemy.Move(current_level_array,(self.player.PlayerRect.centerx,self.player.PlayerRect.centery),current_level_tiles,current_door_tiles)
                        elif (enemy.Name != "Spider" and enemy.Name != "Spider Boss"):
                            enemy.Move(current_level_array,(self.player.PlayerRect.centerx,self.player.PlayerRect.centery),current_level_tiles,current_door_tiles)
        self.render_enemy_bars()
    
    def enemies_attack(self):
        # Enemies attack the player and shoots a bullet at the player
        player_pos = ((self.player.PlayerRect.centerx),(self.player.PlayerRect.centery))
        Enemies = self.current_q.queue
        for enemy in Enemies:
            enemy_rect = enemy.EnemyRect
            if enemy != None:
                if enemy.state == "active":
                    if enemy.Name != "Ghost" and enemy.Name != "Skeleton" and enemy.Name != "Ghost Boss" and enemy.Name != "Skeleton Boss":
                        if enemy.can_attack() and not(self.player.Status_Effects["Invisible"]):
                            if enemy.start:
                                enemy.Attack(player_pos)
                    # Checks if the enemy collides with the player
                    if enemy_rect.colliderect(self.player.PlayerRect):
                        # Makes sure continuous damage is not taken when colliding
                        if not self.player.invincible:
                            self.player.Health -= enemy.Strength
                            self.player.last_hit_time = pygame.time.get_ticks()
                            self.player.invincible = True
 
    def check_collision_bullet_player(self,current_level_tiles):
        # Checks if the players bullets have collided with walls or an enemy
        Enemies = self.current_q.queue
        for b in self.player.projectiles:
                delete = b.check_collision_walls(current_level_tiles)
                if delete:
                    self.player.projectiles.remove(b)
        for enemy in Enemies:
            for b in self.player.projectiles:
                if enemy != None and enemy.state == "active":
                    enemy_damage = b.check_collision_entity(enemy.EnemyRect)
                    if enemy_damage:
                        final_damage = enemy.TakeDamage(b.damage,self.player.armor_penetration)
                        enemy.Health -= final_damage
                        self.player.projectiles.remove(b)
        self.check_enemies_dead()
    
    def check_collision_bullet_enemy(self,current_level_tiles):
        # Checks if enemies bullets have collided with the player or the walls
        Enemies = self.current_q.queue
        for enemy in Enemies:
            if enemy.Name != "Ghost" and enemy.Name != "Skeleton" and enemy.Name != "Ghost Boss" and enemy.Name != "Skeleton Boss":
                enemy.check_collision_wall(current_level_tiles)
                damage_taken = enemy.check_collision_bullet_player(self.player.PlayerRect)
                final_damage = self.player.TakeDamage(damage_taken)
                if damage_taken > 0:
                    self.player.check_status_effects(enemy)
                self.player.Health -= final_damage
                                
    def assign_enemies_room(self,dict_rooms_empty,number_rooms,no_per_room):
        # Creates enemies for each room
        rooms = self.create_enemies(number_rooms,no_per_room)
        counter = 0
        for room in dict_rooms_empty:
            if self.Levels.boss_room_pos == room:
                #Call the function create_boss_enemies to get the boss enemy then call the create enemies to get enemies for that rooms
                boss_room = (self.create_boss_enemies(no_per_room))[0]
                dict_rooms_empty[room] = boss_room
            # Appends a enemies to the room
            else:
                dict_rooms_empty[room] = rooms[counter]
            counter += 1
        return dict_rooms_empty
    
    def create_enemies(self,number_rooms,no_per_room):
        # For a number of rooms in creates a q of a certain number of enemies
        rooms = []
        for i in range(number_rooms):
            rooms.append(Queue(no_per_room))
        for q in rooms:
            for x in range(no_per_room):
                enemy_selected = random.choices(self.enemy_names, weights = (40,40,20,20,20))
                random_pos = (random.randint(128,1500),random.randint(135,600))
                if self.difficulty == "Easy":
                    health = random.randint(100,150)
                    strength = random.randint(1,5)
                    defence = random.randint(25,50)
                    acd_spider = 14 + random.random()
                    acd_other = 10 + random.random()
                if self.difficulty == "Medium":
                    health = random.randint(200,250)
                    strength = random.randint(10,20)
                    defence = random.randint(50,75)
                    acd_spider = 10 + random.random()
                    acd_other = 5 + random.random()
                if self.difficulty == "Hard":
                    health = random.randint(300,350)
                    strength = random.randint(20,30)
                    defence = random.randint(75,100)
                    acd_spider = 5 + random.random()
                    acd_other = 3 + random.random()
                if enemy_selected == ['Water']:
                    enemy_selected = Water_Monster(health,"Water",strength,defence,2,acd_other,random_pos)
                if enemy_selected == ['Skeleton']:
                    enemy_selected = Enemy(health,"Skeleton",strength,defence,2,0,random_pos)
                    #Create Enemy Skeleton object
                if enemy_selected == ['Ghost']:
                    #Create Enemy Ghost object
                    enemy_selected = Enemy(health,"Ghost",strength,defence,2,0,random_pos)
                if enemy_selected == ['Spider']:
                    #Create Enemy Spider Object
                    enemy_selected = Spider(health,"Spider",strength,defence,2,acd_spider,random_pos)
                if enemy_selected == ['Fire']:
                    #Create Enemy Fire Object
                    enemy_selected = Fire_Monster(health,"Fire",strength,defence,2,acd_other,random_pos)
                q.Enqueue(enemy_selected)
        return rooms
    
    def create_boss_enemies(self,no_enemies):
        # Creates a single room and adds the boss enemy to the room
        room = self.create_enemies(1,(no_enemies))
        for q in room:
            enemy_selected = random.choices(self.enemy_names, weights = (40,40,20,20,20))
            random_pos = (random.randint(128,1500),random.randint(135,600))
            if self.difficulty == "Easy":
                health = random.randint(300,350)
                strength = random.randint(10,20)
                defence = random.randint(50,75)
            if self.difficulty == "Medium":
                health = random.randint(400,450)
                strength = random.randint(20,30)
                defence = random.randint(75,100)
            if self.difficulty == "Hard":
                health = random.randint(500,550)
                strength = random.randint(30,40)
                defence = random.randint(100,125)
            if enemy_selected == ['Water']:
                enemy_selected = Water_Monster(health,"Water Boss",strength,defence,2,3,random_pos)
            if enemy_selected == ['Skeleton']:
                enemy_selected = Enemy(health,"Skeleton Boss",strength,defence,2,0,random_pos)
                #Create Enemy Skeleton object
            if enemy_selected == ['Ghost']:
                #Create Enemy Ghost object
                enemy_selected = Enemy(health,"Ghost Boss",strength,defence,2,0,random_pos)
            if enemy_selected == ['Spider']:
                #Create Enemy Spider Object
                enemy_selected = Spider(health,"Spider Boss",strength,defence,2,5,random_pos)
            if enemy_selected == ['Fire']:
                #Create Enemy Fire Object
                enemy_selected = Fire_Monster(health,"Fire Boss",strength,defence,2,3,random_pos)
            q.Dequeue()
            q.queue[0] = enemy_selected
        return room
    
    def check_collision_door(self,door_tile):
        # Checks which door the player collidede with and where the player collided with the door and changes the room
        for d in door_tile:
            if self.player.PlayerRect.colliderect(d):
                if d.collidepoint(self.player.PlayerRect.center) and self.player.PlayerRect.x < 560:
                    #left
                    self.current_x -= 1
                    self.player.player_reset()
                    self.current_q = self.enemy_rooms[(self.current_y,self.current_x)]
                    self.reset_enemy_start()
                    cleared = self.check_all_enemies_cleared_room(self.current_q.queue)
                    #Need to reset the level
                    self.Levels.reset_all_rooms((self.current_y,self.current_x))
                    if cleared:
                        self.same_room = True
                    else:
                        self.same_room = False
                if d.collidepoint(self.player.PlayerRect.center) and self.player.PlayerRect.x > 1360:
                    #right
                    self.current_x += 1
                    self.player.player_reset()
                    self.current_q = self.enemy_rooms[(self.current_y,self.current_x)]
                    self.reset_enemy_start()
                    cleared = self.check_all_enemies_cleared_room(self.current_q.queue)
                    #Need to reset the level
                    self.Levels.reset_all_rooms((self.current_y,self.current_x))
                    if cleared:
                        self.same_room = True
                    else:
                        self.same_room = False
                if d.collidepoint(self.player.PlayerRect.center) and self.player.PlayerRect.y < 340:
                    #up
                    self.current_y -= 1
                    self.player.player_reset()
                    self.current_q = self.enemy_rooms[(self.current_y,self.current_x)]
                    self.reset_enemy_start()
                    cleared = self.check_all_enemies_cleared_room(self.current_q.queue)
                    #Need to reset the level
                    self.Levels.reset_all_rooms((self.current_y,self.current_x))
                    if cleared:
                        self.same_room = True
                    else:
                        self.same_room = False
                if d.collidepoint(self.player.PlayerRect.center) and self.player.PlayerRect.y > 740:
                    #down
                    self.current_y += 1
                    self.player.player_reset()
                    self.current_q = self.enemy_rooms[(self.current_y,self.current_x)]
                    self.reset_enemy_start()
                    cleared = self.check_all_enemies_cleared_room(self.current_q.queue)
                    #Need to reset the level
                    self.Levels.reset_all_rooms((self.current_y,self.current_x))
                    if cleared:
                        self.same_room = True
                    else:
                        self.same_room = False
       
while True:
    Main_game = Game()
    Main_game.Main()
from Scripts.Entities import PhysicsEntity, Entity
import random
import pygame
from Scripts.particle import Particle
import math
import logging

logging.basicConfig(level=logging.CRITICAL)

#############################################
###########    PLAYER CLASS    ##############
#############################################
class Player(PhysicsEntity):

    # Define the Player inheriting from Physics Entity
    def __init__(self, game, pos, size, speed=1, max_health=1, max_jumps=1, health=1):
        super().__init__(game, "player", pos, size, speed)
        self.wall_slide = False
        self.max_jumps = max_jumps
        self.air_time = 0
        self.jumps = 2
        self.dashing = [0, 0]
        self.charging = 0
        self.attacking = 0
        self.death = 0
        self.max_health = max_health
        self.health = health
        self.slashes = []
        self.inventory = [0, 1, 2, 3, 4, 5, 6, 7,
                          8, 9, 10, 11, 12, 13, 14, 15]
        self.jump_cooldown = 0
        self.double_jumped = 0
        self.coins = 0
        self.particles = []
        self.iframes = 0

    def draw_hitbox(self):
        if self.dashing[0] == 0 and self.dashing[1] == 0:
            pygame.draw.rect(self.game.display, (255, 0, 0), (self.pos[0] - self.game.scroll[0] - self.leeway[0] / 2,
                                                              self.pos[1] - self.game.scroll[1] - self.leeway[1] / 2,
                                                              self.rect().width + self.leeway[0],
                                                              self.rect().height + self.leeway[1]), 1)
        elif self.dashing[0] <= 30 and self.dashing[1] <= 30:
            # draw a circle around the player
            pygame.draw.circle(self.game.display, (255, 0, 0), (self.pos[0] - self.game.scroll[0] + self.rect().width // 2, self.pos[1] - self.game.scroll[1] + self.rect().height // 2), 10, 1)

    # Main Player Update Function (Overriden)
    def update(self, tilemap, movement=(0, 0), speed=1):
        super().update(tilemap, movement=movement)

        self.speed = speed
        self.air_time += 1
        self.wall_slide = False

        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
        if self.charging > 0:
            self.charging += 1
        self.iframes = max(0, self.iframes - 1)

        self.handle_charging_particles()


        if movement[0] != 0:
            if abs(self.dashing[0]) > 30:
                self.scale_speed = min(1.25, self.scale_speed + 0.03)
            else:
                self.scale_speed = min(1, self.scale_speed + 0.03)
        else:
            self.scale_speed = max(0.3, self.scale_speed - 0.08)

        if self.air_time > 160:  # time before despawning from fall
            self.health = 0
            self.game.screenshake = max(16, self.game.screenshake)
            logging.debug('Despawned due to great fall')


        if self.collisions['down']:
            self.air_time = 0
            self.jumps = self.max_jumps
            self.wall_slide = False

        # Wall Slide Handling
        if (self.collisions['left'] or self.collisions['right']) and self.air_time > 4 and self.game.collectables['Wall Climb'] == True:
            self.wall_slide = True
            self.air_time -= 1  # to prevent from despawning after a long wall slide
            self.velocity[1] = min(self.velocity[1], 0.5)

        if self.attacking > 0:
            if self.wall_slide:
                self.set_action("wall_slide")
            elif self.air_time > 4:
                self.set_action("jump")
            elif movement[0] != 0:
                self.set_action("run")
            else:
                self.set_action("idle")
        else:
            if self.wall_slide:
                self.set_action("sword_wall_slide")
            elif self.air_time > 4:
                self.set_action("sword_jump")
            elif movement[0] != 0:
                self.set_action("sword_run")
            else:
                self.set_action("sword_idle")



        # Deal with Particles for Dash
        if abs(self.dashing[0]) in {60, 50} or abs(self.dashing[1]) in {90, 80}:
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed,
                             math.sin(angle) * speed]  # Speed for directional movement at an angle
                self.game.particles.append(
                    Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))

        for i in range(2):
            if self.dashing[i] > 0:
                self.dashing[i] = max(0, self.dashing[i] - 1)
            elif self.dashing[i] < 0:
                self.dashing[i] = min(0, self.dashing[i] + 1)


        # Common logic for both dashes
        for i in range(2):

            # sets the threshold for the dash depending on the direction of the dash (0 = horizontal, 1 = vertical)
            abs_dashing = abs(self.dashing[i])
            threshold = 50 if i == 0 else 80
            velocity_factor = 3 if i == 0 else 7.5
            velocity_modifier = 0.2 if i == 0 else 0.3

            if abs_dashing > threshold:
                self.velocity[i] = abs_dashing / self.dashing[i] * velocity_factor

                if abs_dashing == threshold + 1:
                    self.velocity[i] *= velocity_modifier

                pvelocity = [0, 0]
                pvelocity[i] = abs_dashing / self.dashing[i] * random.random() * 3
                self.game.particles.append(
                    Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7))
                )

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        elif self.velocity[0] < 0:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)
        self.attacking = max(0, self.attacking - 1)

        for slash in self.slashes:
            slash.update(self.game.tilemap)

            if slash.powerful:
                slash.render(self.game.display, offset=self.game.render_scroll)
                print("rendering powerful slash at", slash.pos)
            else:
                slash.flip = self.flip
                if self.flip:
                    slash.pos = (self.pos[0] - 12, self.pos[1])
                    slash.render(self.game.display, offset=self.game.render_scroll)

                elif not self.flip:
                    slash.pos = (self.pos[0] + 12, self.pos[1])
                    slash.render(self.game.display, offset=self.game.render_scroll)

            if slash.done:
                self.slashes.remove(slash)

    # Main Player Render Function (Overriden)
    def render(self, surf, offset=(0, 0)):
        if self.iframes > 0:
            if (self.iframes // 4) % 4 == 0:  # Group frames in pairs of 2
                return
        # First render the charging particles
        particles_to_remove = []
        for particle in self.particles:
            if particle.type == 'charge_particle':
                particle.pos[0] += particle.velocity[0]
                particle.pos[1] += particle.velocity[1]

                # Calculate the offset based on movement speed
                base_offset = 8
                movement_scale = self.scale_speed if self.scale_speed > 0.3 else 0
                x_adjust = base_offset * movement_scale * (1 if self.flip else -1)

                # Calculate distance to the offset-adjusted player position
                player_center_x = self.pos[0] + self.rect().width / 2 + x_adjust
                player_center_y = self.pos[1] + self.rect().height / 2

                dx = player_center_x - particle.pos[0]
                dy = player_center_y - particle.pos[1]
                dist = math.sqrt(dx * dx + dy * dy)

                # Scale the distance threshold based on movement speed
                base_threshold = 3
                speed_multiplier = max(1, self.scale_speed * 5)  # Increase threshold when moving
                removal_threshold = base_threshold * speed_multiplier

                if dist < removal_threshold or particle.age > 30:
                    particles_to_remove.append(particle)

                particle.update()
                render_offset = (offset[0] + x_adjust, offset[1])
                particle.render(surf, offset=render_offset)

        # Then render the player sprite on top if not in long dash
        if abs(self.dashing[0]) <= 50:
            super().render(surf, offset=offset)

        # Clean up any particles that need to be removed
        for particle in particles_to_remove:
            self.particles.remove(particle)


    # Main Player Jump Function
    def jump(self, strength=1):
        if self.jump_cooldown > 0 and self.double_jumped > 0:
            return False


        elif self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 2.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True

            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -2.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True


        elif self.jumps > 0:
            self.velocity[1] = -3 * strength
            self.jumps -= 1
            self.air_time = 5
            return True

    # Player Dash Function
    def dash(self, up=False, down=False):
        if self.game.collectables['Dash'] == True:
            logging.info("Dash called, flip is: " + str(self.flip) + " and abs movement = " + str(abs(self.game.movement[0])))
            if self.dashing[0] == 0 and self.dashing[1] == 0:
                self.scale_speed = 1.25     # burst of acceleration after dash to get to higher than max speed
                self.game.sfx['dash'].play()
                self.air_time = max (0, self.air_time - 80)

                #   Vertical Dash
                if self.game.up:
                    self.dashing[1] = -90
                elif self.game.down:
                    self.dashing[1] = 90

                #   Movement Dash
                elif self.game.movement[0] > 0 or self.game.movement[1] > 0:
                    self.velocity[1] = -0.75
                    if self.flip:
                        self.dashing[0] = -60  # cooldown
                        logging.info("Dash left")
                    elif not self.flip:
                        self.dashing[0] = 60  # cooldown
                        logging.info("Dash right")

                #   Standing Dash
                elif self.game.movement[0] == 0 and self.game.movement[1] == 0:
                    self.velocity[1] = -0.75
                    if self.flip:
                        self.dashing[0] = -60
                        logging.info("Dash left")
                    elif not self.flip:
                        self.dashing[0] = 60
                        logging.info("Dash right")

    def attack(self, powerful=False):
        if powerful:
            self.attacking = 25
            self.slashes.append(Entity(self.game, "slash", (self.rect().x, self.rect().y), size=(8, 16), leeway=(0, 0), velocity=[-3 if self.flip else 3, 0], powerful=True, lifetime=5))
            print("Powerful Attack with velocity of", self.velocity)
        elif not self.attacking:
            self.attacking = 25
            self.slashes.append(Entity(self.game, "slash", self.rect().center, size=(8, 16),  leeway=(0, 0)))
            print("Normal Attack")

    def handle_charging_particles(self):
        if 20 <= self.charging < 70:
            if self.charging == 20:
                self.game.sfx['charging'].play()
            for i in range(3):
                spawn_radius = 30
                angle = random.random() * math.pi * 2
                spawn_x = self.pos[0] + self.rect().width / 2 + math.cos(angle) * spawn_radius
                spawn_y = self.pos[1] + self.rect().height / 2 + math.sin(angle) * spawn_radius

                dx = (self.pos[0] + self.rect().width / 2) - spawn_x
                dy = (self.pos[1] + self.rect().height / 2) - spawn_y
                dist = math.sqrt(dx * dx + dy * dy)
                speed = 0.75
                pvelocity = [dx / dist * speed, dy / dist * speed]

                self.particles.append(
                    Particle(self.game, 'charge_particle', [spawn_x, spawn_y],
                             velocity=pvelocity, frame=random.randint(3, 3)))
        elif self.charging >= 70:
            if self.charging == 70:
                self.game.sfx['charging'].stop()
                self.game.sfx['charged'].play()
            self.particles = []
            #create sparks for powerful attack
            if self.charging % 3 == 0: #    3 is the number of frames between each spark
                # make sure the angle is only between 0 and 180 degrees
                angle = random.random() * math.pi
                speed = random.random() * 0.2 + 0.2
                pvelocity = [math.cos(angle) * speed,
                             math.sin(angle) * speed]
                self.game.particles.append(
                    Particle(self.game, 'charge_particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))


    # Simple Heatlh/Damage Function
    def hurt(self, damage=1):
        #TODO: Add dodge sound effect
        self.game.sfx['hit'].play()
        if self.iframes <= 0:
            logging.info("Ouch! I got hit for " + str(damage) + " damage!")
            self.health -= 1
            self.iframes = 90

    def start_charging(self):
        self.charging = 1


    def stop_charging(self):
        self.particles = []
        self.game.sfx['charging'].stop()
        self.game.sfx['charged'].stop()
        if self.charging >= 70:
            self.attack(powerful=True)
        print(self.charging)
        self.charging = 0



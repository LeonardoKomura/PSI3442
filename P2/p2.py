#!/usr/bin/python3
# -*- coding:utf-8 -*-

import rospy
import random
from geometry_msgs.msg import PoseStamped
from mavros_msgs.srv import SetMode, CommandBool
from mavros_msgs.msg import State

rospy.init_node("launch")

# Objetos de comandos e estados
current_state = State()
current_pose = PoseStamped()
goal_pose = PoseStamped()

def state_callback(msg):
    global current_state
    current_state = msg

def pose_callback(msg):
    global current_pose
    current_pose = msg

# Objetos de Service, Publisher e Subscriber
arm = rospy.ServiceProxy('/mavros/cmd/arming', CommandBool)
set_mode_srv = rospy.ServiceProxy('/mavros/set_mode', SetMode)
local_position_pub = rospy.Publisher('/mavros/setpoint_position/local', PoseStamped, queue_size=10)
state_sub = rospy.Subscriber("/mavros/state", State, state_callback)
pose_sub = rospy.Subscriber("/mavros/local_position/pose", PoseStamped, pose_callback)

# Frequência de publicação do setpoint
rate = rospy.Rate(20)

# Espera a conexão ser iniciada
print("Esperando conexão com FCU")
while not rospy.is_shutdown() and not current_state.connected:
    rate.sleep()
    
# Publica algumas mensagens antes de trocar o modo de voo
for i in range(100):
    local_position_pub.publish(goal_pose)
    rate.sleep()

# Coloca no modo Offboard
last_request = rospy.Time.now()
if (current_state.mode != "OFFBOARD"):
    result = set_mode_srv(0, "OFFBOARD")
    print("Alterando para modo Offboard")
    while not rospy.is_shutdown() and current_state.mode != "OFFBOARD" and (rospy.Time.now() - last_request > rospy.Duration(1.0)):
        result = set_mode_srv(0, "OFFBOARD")
    print("Drone em modo Offboard")
else:
    print("Drone já está em modo Offboard")
    
# Arma o drone
if (not current_state.armed):
    result = arm(True)
    print("Armando o drone")
    while not rospy.is_shutdown() and not current_state.armed:
        result = arm(True)
    print("Drone armado")
else:
    print("Drone já armado")
    
# Criando a posição fictícia de balão (área de 100x100 em relação ao local de lançamento)
target_x = random.randint(10, 100)
target_y = random.randint(10, 100)
target_z = 50
print("Posição aproximada do balão: (%d, %d, %d)" % (target_x, target_y, target_z))

# Comandos de movimentação
TOL=0.5
print("Decolando")
goal_pose.pose.position.z = 10
while not rospy.is_shutdown() and abs(goal_pose.pose.position.z - current_pose.pose.position.z) > TOL:
    local_position_pub.publish(goal_pose)
    rate.sleep()
    
print("Esperando")
t0 = rospy.Time.now()
while not rospy.is_shutdown() and rospy.Time.now() - t0 < rospy.Duration(5):
    local_position_pub.publish(goal_pose)
    rate.sleep()
    
goal_pose.pose.position.x = target_x -1
goal_pose.pose.position.y = target_y -1
goal_pose.pose.position.z = target_z
print("Indo ao objetivo")
while not rospy.is_shutdown() and rospy.Time.now() - t0 < rospy.Duration(10) and (abs(goal_pose.pose.position.x-current_pose.pose.position.x)>TOL) and (abs(goal_pose.pose.position.y-current_pose.pose.position.y)>TOL) and (abs(goal_pose.pose.position.z-current_pose.pose.position.z)>TOL):
    randx = random.randint(0,100); randx -= 50; randx = randx/10000
    randy = random.randint(0,100); randy -= 50; randy = randy/10000
    randz = random.randint(0,100); randx = randx/1000
    
    target_x += randx
    target_y += randy
    target_z += randz
    
    goal_pose.pose.position.x = target_x 
    goal_pose.pose.position.y = target_y 
    goal_pose.pose.position.z = target_z 
    
    local_position_pub.publish(goal_pose)
    rate.sleep()
    
print("Coordenadas em que ele encontrou o balão: (%f, %f)" % (current_pose.pose.position.x, current_pose.pose.position.y))
print("Seguindo o balão")
TOL=0.1
t0 = rospy.Time.now()
while not rospy.is_shutdown() and rospy.Time.now() - t0 < rospy.Duration(10) and (abs(goal_pose.pose.position.x-current_pose.pose.position.x)>TOL) and (abs(goal_pose.pose.position.y-current_pose.pose.position.y)>TOL) and (abs(goal_pose.pose.position.z-current_pose.pose.position.z)>TOL):
    randx = random.randint(0,100); randx -= 50; randx = randx/100000
    randy = random.randint(0,100); randy -= 50; randy = randy/100000
    randz = random.randint(0,100); randx = randx/10000
    
    target_x += randx
    target_y += randy
    target_z += randz
    
    goal_pose.pose.position.x = target_x 
    goal_pose.pose.position.y = target_y 
    goal_pose.pose.position.z = target_z 
    
    local_position_pub.publish(goal_pose)
    
    local_position_pub.publish(goal_pose)
    rate.sleep()

print("Afastando-se do balão:")
goal_pose.pose.position.x = target_x - 5
goal_pose.pose.position.y = target_y - 5
while not rospy.is_shutdown() and (abs(goal_pose.pose.position.x - current_pose.pose.position.x) > TOL) and (abs(goal_pose.pose.position.y - current_pose.pose.position.y) > TOL):
    local_position_pub.publish(goal_pose)
    rate.sleep()

print("Esperando")
t0 = rospy.Time.now()
while not rospy.is_shutdown() and rospy.Time.now() - t0 < rospy.Duration(5):
    local_position_pub.publish(goal_pose)
    rate.sleep()

print("Voltando para o ponto de lançamento:")
goal_pose.pose.position.x = 0
goal_pose.pose.position.y = 0
goal_pose.pose.position.z = 10
while not rospy.is_shutdown() and (abs(goal_pose.pose.position.x - current_pose.pose.position.x) > TOL) and (abs(goal_pose.pose.position.y - current_pose.pose.position.y) > TOL):
    local_position_pub.publish(goal_pose)
    rate.sleep()

# Coloca no modo Land
if (current_state.mode != "AUTO.LAND"):
    result = set_mode_srv(0, "AUTO.LAND")
    print("Alterando para modo Land")
    while not rospy.is_shutdown() and current_state.mode != "AUTO.LAND":
        result = set_mode_srv(0, "AUTO.LAND")
    print("Drone em modo Land")
else:
    print("Drone já está em modo Land")
    
print("Coordenada final do drone: (%f, %f)" % (current_pose.pose.position.x, current_pose.pose.position.y))
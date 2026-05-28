import math
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QPainterPath, QFont
from PyQt6.QtCore import Qt, QPointF, QRectF

def get_icon_pixmap(name, color_hex, size=24):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    if pixmap.isNull():
        return pixmap
        
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    color = QColor(color_hex)
    pen = QPen(color)
    pen.setWidthF(2.0)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    
    # Escalar coordenadas basado en el estándar 24x24
    scale = size / 24.0
    painter.scale(scale, scale)
    
    if name == "home":
        # Casa moderna minimalista
        path = QPainterPath()
        path.moveTo(3, 10)
        path.lineTo(12, 3)
        path.lineTo(21, 10)
        path.moveTo(5, 9.5)
        path.lineTo(5, 21)
        path.lineTo(19, 21)
        path.lineTo(19, 9.5)
        path.moveTo(9, 21)
        path.lineTo(9, 14)
        path.lineTo(15, 14)
        path.lineTo(15, 21)
        painter.drawPath(path)
        
    elif name == "exercises" or name == "dumbbell":
        # Mancuerna deportiva premium
        painter.drawLine(4, 12, 20, 12)
        painter.drawLine(6, 8, 6, 16)
        painter.drawLine(8, 6, 8, 18)
        painter.drawLine(16, 6, 16, 18)
        painter.drawLine(18, 8, 18, 16)
        
    elif name == "stats" or name == "chart":
        # Gráfico de barras ascendente
        painter.drawLine(6, 18, 6, 12)
        painter.drawLine(12, 18, 12, 6)
        painter.drawLine(18, 18, 18, 9)
        painter.drawLine(3, 20, 21, 20)
        
    elif name == "settings" or name == "cog":
        # Engranaje limpio de configuración
        painter.drawEllipse(7, 7, 10, 10)
        painter.drawEllipse(10, 10, 4, 4)
        teeth = [
            (12, 5), (12, 19), (5, 12), (19, 12),
            (7.5, 7.5), (16.5, 16.5), (7.5, 16.5), (16.5, 7.5)
        ]
        for tx, ty in teeth:
            dx = 12 - tx
            dy = 12 - ty
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                ux = dx / dist
                uy = dy / dist
                painter.drawLine(
                    QPointF(tx, ty), 
                    QPointF(tx + ux * 1.5, ty + uy * 1.5)
                )
                
    elif name == "logout":
        # Icono de salida / Cerrar sesión
        path = QPainterPath()
        path.moveTo(14, 3)
        path.lineTo(4, 3)
        path.lineTo(4, 21)
        path.lineTo(14, 21)
        painter.drawPath(path)
        painter.drawLine(9, 12, 20, 12)
        painter.drawLine(17, 9, 20, 12)
        painter.drawLine(17, 15, 20, 12)
        
    elif name == "star" or name == "points":
        # Estrella simétrica premium
        path = QPainterPath()
        pts = [
            (12, 3), (15.5, 9), (22, 10.5), (17.5, 15), 
            (19, 21.5), (12, 18.5), (5, 21.5), (6.5, 15), 
            (2, 10.5), (8.5, 9)
        ]
        path.moveTo(pts[0][0], pts[0][1])
        for px, py in pts[1:]:
            path.lineTo(px, py)
        path.closeSubpath()
        painter.drawPath(path)
        
    elif name == "level" or name == "trophy":
        # Trofeo elegante
        path = QPainterPath()
        path.moveTo(6, 4)
        path.lineTo(18, 4)
        path.lineTo(17, 12)
        path.quadTo(12, 16, 7, 12)
        path.closeSubpath()
        painter.drawPath(path)
        painter.drawLine(12, 15, 12, 19)
        painter.drawLine(8, 20, 16, 20)
        # Asas del trofeo
        painter.drawArc(QRectF(3.5, 5, 5, 5), 90 * 16, 180 * 16)
        painter.drawArc(QRectF(15.5, 5, 5, 5), 270 * 16, 180 * 16)
        
    elif name == "streak" or name == "fire":
        # Rayo de actividad / streak
        path = QPainterPath()
        path.moveTo(13, 2)
        path.lineTo(6, 12)
        path.lineTo(12, 12)
        path.lineTo(11, 22)
        path.lineTo(18, 12)
        path.lineTo(12, 12)
        path.closeSubpath()
        painter.drawPath(path)
        
    elif name == "play":
        # Botón de reproducir/iniciar
        path = QPainterPath()
        path.moveTo(8, 5)
        path.lineTo(19, 12)
        path.lineTo(8, 19)
        path.closeSubpath()
        painter.drawPath(path)
        
    elif name == "arrow_down" or name == "down":
        # Flecha/Chevron hacia abajo
        path = QPainterPath()
        path.moveTo(6, 9)
        path.lineTo(12, 15)
        path.lineTo(18, 9)
        painter.drawPath(path)
        
    elif name == "arrow_up" or name == "up":
        # Flecha/Chevron hacia arriba
        path = QPainterPath()
        path.moveTo(6, 15)
        path.lineTo(12, 9)
        path.lineTo(18, 15)
        painter.drawPath(path)
        
    elif name == "equal" or name == "line" or name == "dash":
        # Raya horizontal
        painter.drawLine(6, 12, 18, 12)
        
    elif name == "check":
        # Marca de verificación / checkmark
        path = QPainterPath()
        path.moveTo(4, 12)
        path.lineTo(10, 17)
        path.lineTo(20, 6)
        painter.drawPath(path)
        
    elif name == "document" or name == "info" or name == "terms":
        # Documento / términos
        painter.drawRect(5, 3, 14, 18)
        painter.drawLine(8, 7, 16, 7)
        painter.drawLine(8, 11, 16, 11)
        painter.drawLine(8, 15, 12, 15)
        
    elif name == "google":
        # G de Google
        path = QPainterPath()
        path.moveTo(19, 11)
        path.lineTo(12, 11)
        path.lineTo(12, 13.5)
        path.lineTo(16.5, 13.5)
        path.arcTo(QRectF(5, 5, 14, 14), 335, -290)
        painter.drawPath(path)
        
    elif name == "camera":
        # Cámara de fotos / webcam
        painter.drawRect(4, 7, 16, 12)
        path = QPainterPath()
        path.moveTo(9, 7)
        path.lineTo(10, 4)
        path.lineTo(14, 4)
        path.lineTo(15, 7)
        painter.drawPath(path)
        painter.drawEllipse(9, 10, 6, 6)

    elif name == "key" or name == "password":
        # Llave de seguridad
        painter.drawEllipse(5, 10, 6, 6)
        painter.drawLine(11, 13, 20, 13)
        painter.drawLine(16, 13, 16, 16)
        painter.drawLine(19, 13, 19, 16)
        
    elif name == "user" or name == "profile":
        # Perfil de usuario
        painter.drawEllipse(8, 4, 8, 8)
        path = QPainterPath()
        path.arcTo(QRectF(4, 14, 16, 10), 180, -180)
        painter.drawPath(path)
        
    elif name == "clock" or name == "time":
        # Reloj analógico minimalista
        painter.drawEllipse(4, 4, 16, 16)
        painter.drawLine(12, 12, 12, 7)
        painter.drawLine(12, 12, 15, 12)
        
    elif name == "squat":
        # Silueta sentadillas
        painter.drawEllipse(10, 4, 4, 4)
        path = QPainterPath()
        path.moveTo(12, 8)
        path.lineTo(10, 13)
        path.lineTo(15, 16)
        path.lineTo(9, 21)
        path.moveTo(11, 10)
        path.lineTo(17, 10)
        painter.drawPath(path)
        
    elif name == "pushup":
        # Silueta lagartijas
        painter.drawEllipse(5, 11, 4, 4)
        path = QPainterPath()
        path.moveTo(7, 13)
        path.lineTo(19, 17)
        path.moveTo(9, 13.5)
        path.lineTo(9, 18)
        path.moveTo(19, 17)
        path.lineTo(20, 18)
        painter.drawPath(path)
        
    elif name == "jumping_jacks" or name == "jack":
        # Silueta jumping jacks
        painter.drawEllipse(10, 3, 4, 4)
        path = QPainterPath()
        path.moveTo(12, 7)
        path.lineTo(12, 13)
        path.moveTo(12, 9)
        path.lineTo(5, 5)
        path.moveTo(12, 9)
        path.lineTo(19, 5)
        path.moveTo(12, 13)
        path.lineTo(6, 21)
        path.moveTo(12, 13)
        path.lineTo(18, 21)
        painter.drawPath(path)

    elif name == "eye":
        # Ojo outline para contraseñas
        path = QPainterPath()
        path.moveTo(3, 12)
        path.quadTo(12, 4, 21, 12)
        path.quadTo(12, 20, 3, 12)
        painter.drawPath(path)
        painter.drawEllipse(10, 10, 4, 4)

    elif name == "lock":
        # Padlock outline
        painter.drawRect(6, 10, 12, 9)
        path = QPainterPath()
        path.moveTo(8, 10)
        path.lineTo(8, 7)
        path.quadTo(12, 3, 16, 7)
        path.lineTo(16, 10)
        painter.drawPath(path)
        painter.drawEllipse(11, 13, 2, 2)

    elif name == "shield" or name == "security":
        # Draw a beautiful security shield
        path = QPainterPath()
        path.moveTo(12, 3)
        path.lineTo(19, 6)
        path.lineTo(19, 12)
        path.quadTo(19, 18, 12, 21)
        path.quadTo(5, 18, 5, 12)
        path.lineTo(5, 6)
        path.closeSubpath()
        painter.drawPath(path)

    elif name == "at":
        # Draw @ symbol beautifully
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(0, 0, 24, 24), Qt.AlignmentFlag.AlignCenter, "@")

    painter.end()
    return pixmap

def get_icon(name, color_hex, size=24):
    pixmap = get_icon_pixmap(name, color_hex, size)
    return QIcon(pixmap)

def get_state_icon(name, normal_color, active_color, checked_color, size=24):
    icon = QIcon()
    # Estado normal, no seleccionado
    icon.addPixmap(get_icon_pixmap(name, normal_color, size), QIcon.Mode.Normal, QIcon.State.Off)
    # Estado seleccionado (checked)
    icon.addPixmap(get_icon_pixmap(name, checked_color, size), QIcon.Mode.Normal, QIcon.State.On)
    # Estado activo / hover
    icon.addPixmap(get_icon_pixmap(name, active_color, size), QIcon.Mode.Active, QIcon.State.Off)
    icon.addPixmap(get_icon_pixmap(name, active_color, size), QIcon.Mode.Active, QIcon.State.On)
    return icon

import random

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QPixmap, QImage, QColor
from PySide6.QtWidgets import QWidget, QSizePolicy, QVBoxLayout
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtOpenGL import QOpenGLShaderProgram, QOpenGLShader, QOpenGLTexture
from OpenGL import GL

from lib.quol_window import QuolBaseWindow
from lib.quol_transition import QuolTransition
from lib.transition_loader import TransitionInfo


class ShaderTransition(QuolTransition, QWidget):
    def __init__(self, transition_info: TransitionInfo, window: QuolBaseWindow, vertex_source: str, fragment_src: str):
        QuolTransition.__init__(self, transition_info, window)
        QWidget.__init__(self, window)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.shader_widget = TextureShaderWidget(vertex_source, fragment_src)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.shader_widget)

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_overlay)
        self.update_timer.setInterval(10)

        # initialize gl context
        self.show()
        self.hide()

    def update_overlay(self):
        if self.shader_widget.is_done():
            # self.hide()
            if not self.shader_widget.forward:
                self.window.show()
                QTimer.singleShot(50, self.hide)
            else:
                self.hide()
            self.update_timer.stop()

        self.shader_widget.repaint()

    def capture(self):
        self.setGeometry(self.window.geometry())

        render_target = QPixmap(self.window.width(), self.window.height())
        render_target.fill(QColor(0, 0, 0, 0))
        self.window.render(render_target, QPoint(0, 0))

        image = render_target.toImage().mirrored(False, True)
        self.shader_widget.set_texture(image)

    def exit(self):
        self.update_timer.stop()

        self.capture()
        self.show()
        self.window.hide()

        self.shader_widget.forward = True
        self.shader_widget.new_seed()
        self.update_timer.start()

    def enter(self):
        self.update_timer.stop()
        self.show()

        self.shader_widget.forward = False
        self.update_timer.start()


class TextureShaderWidget(QOpenGLWidget):
    def __init__(self, vertex_src: str, fragment_src: str, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.vertex_src = vertex_src
        self.fragment_src = fragment_src

        self.program = None
        self.texture = None
        self.vertex_shader = None
        self.fragment_shader = None

        self.forward = True
        self.count = 0
        self.end = 1

        self.seed = 0
        self.new_seed()

    def new_seed(self):
        self.seed = random.random()

    def set_texture(self, image: QImage):
        self.makeCurrent()

        if self.texture:
            self.texture.destroy()

        self.texture = QOpenGLTexture(image, QOpenGLTexture.MipMapGeneration.DontGenerateMipMaps)
        self.texture.create()

    def is_done(self):
        if self.forward:
            return self.count >= self.end
        else:
            return self.count <= 0

    def initializeGL(self):
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        GL.glClearColor(0, 0, 0, 0)
        GL.glViewport(0, 0, self.width(), self.height())

        self.program = QOpenGLShaderProgram()
        self.program.create()

        self.vertex_shader = QOpenGLShader(QOpenGLShader.ShaderTypeBit.Vertex)
        self.vertex_shader.compileSourceCode(self.vertex_src)
        self.fragment_shader = QOpenGLShader(QOpenGLShader.ShaderTypeBit.Fragment)
        self.fragment_shader.compileSourceCode(self.fragment_src)

        self.program.addShader(self.vertex_shader)
        self.program.addShader(self.fragment_shader)
        self.program.link()

        if self.program.log():
            raise Exception(self.program.log())

    def resizeGL(self, w: int, h: int):
        pass

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        self.program.bind()

        if self.forward:
            self.count += 0.02
        else:
            self.count -= 0.02

        self.program.setUniformValue1f(self.program.uniformLocation("u_time"), self.count)
        self.program.setUniformValue1f(self.program.uniformLocation("u_seed"), self.seed)
        GL.glUniform2f(self.program.uniformLocation("u_res"), self.width(), self.height())

        if self.texture:
            self.texture.bind()
            self.program.setUniformValue1i(self.program.uniformLocation("u_tex"), 0)

        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)
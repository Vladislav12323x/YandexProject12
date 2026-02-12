import arcade


class CustomCRT:
    def __init__(self, width, height, context: arcade.ArcadeContext):
        self.ctx = context
        self.width = max(width, 1)
        self.height = max(height, 1)

        tex_filter = (self.ctx.LINEAR, self.ctx.LINEAR)

        self.texture = self.ctx.texture(
            (self.width, self.height),
            components=4,
            filter=tex_filter
        )

        self.framebuffer = self.ctx.framebuffer(color_attachments=[self.texture])
        self.geometry = arcade.gl.geometry.quad_2d_fs()

        vertex_shader = """
        #version 330
        in vec2 in_vert;
        in vec2 in_uv;
        out vec2 v_uv;
        void main() {
            gl_Position = vec4(in_vert, 0.0, 1.0);
            v_uv = in_uv;
        }
        """

        fragment_shader = """
        #version 330
        uniform sampler2D u_texture;
        uniform vec2 u_resolution;
        in vec2 v_uv;
        out vec4 f_color;

        vec2 curve(vec2 uv) {
            uv = (uv - 0.5) * 2.0;
            uv.x *= 1.0 + pow((abs(uv.y) / 5.0), 2.0);
            uv.y *= 1.0 + pow((abs(uv.x) / 4.0), 2.0);
            return (uv / 2.0) + 0.5;
        }

        void main() {
            vec2 uv = curve(v_uv);

            if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
                f_color = vec4(0.0, 0.0, 0.0, 1.0);
                return;
            }
            
            vec2 off = 1.0 / u_resolution;
            vec4 color_sum = vec4(0.0);

            for(float i = -1.0; i <= 1.0; i++) {
                for(float j = -1.0; j <= 1.0; j++) {
                    color_sum += texture(u_texture, uv + vec2(i, j) * off);
                }
            }
            vec3 color = color_sum.rgb / 9.0;

            float scanline = sin(uv.y * u_resolution.y * 1.5) * 0.1;
            color -= scanline;

            float vig = 16.0 * uv.x * uv.y * (1.0 - uv.x) * (1.0 - uv.y);
            color *= pow(vig, 0.2);

            f_color = vec4(color * 1.1, 1.0);
        }
        """

        self.program = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
        )

    def use(self):
        self.width = max(self.ctx.window.width, 1)
        self.height = max(self.ctx.window.height, 1)
        self.framebuffer.use()

    def clear(self):
        self.framebuffer.clear()

    def draw(self):
        self.program['u_resolution'] = (float(self.width), float(self.height))
        self.texture.use(0)
        self.geometry.render(self.program)

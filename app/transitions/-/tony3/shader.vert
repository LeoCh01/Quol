#version 330 core

const vec2 positions[6] = vec2[](
    vec2(-1.0, -1.0),
    vec2(1.0, 1.0),
    vec2(-1.0, 1.0),
    vec2(-1.0, -1.0),
    vec2(1.0, 1.0),
    vec2(1.0, -1.0)
);

out vec2 texUV;

void main() {
    texUV = (positions[gl_VertexID] + 1.0f) / 2.0f;
    gl_Position = vec4(positions[gl_VertexID], 0.0, 1.0);
}
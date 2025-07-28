#version 330 core

in vec2 texUV;

uniform float u_time;
uniform vec2 u_res;
uniform sampler2D u_tex;
uniform float u_seed;

float rand(vec2 p)
{
	vec3 p2 = vec3(p.xy,1.0);
    return fract(sin(dot(p2,vec3(37.1,61.7, 12.4)))*3758.5453123);
}

void main()
{
    if(rand(floor(texUV * 10.0f) + vec2(u_seed, 0.0f)) > u_time)
        gl_FragColor = texture(u_tex, texUV);
    else
        gl_FragColor = vec4(0.0f);
}
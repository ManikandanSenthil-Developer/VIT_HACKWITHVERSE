import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export const Hero3D: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Scene
    const scene = new THREE.Scene();

    // Camera
    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    camera.position.z = 32;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Particle Sphere / Financial Intelligence Node Cluster
    const particleCount = 1800;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const purpleColor = new THREE.Color('#8b5cf6');
    const orangeColor = new THREE.Color('#f97316');
    const cyanColor = new THREE.Color('#38bdf8');

    for (let i = 0; i < particleCount; i++) {
      // Fibonacci sphere distribution
      const phi = Math.acos(1 - 2 * (i + 0.5) / particleCount);
      const theta = Math.PI * (1 + Math.sqrt(5)) * (i + 0.5);
      const radius = 13 + (Math.random() - 0.5) * 3.5;

      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = radius * Math.cos(phi);

      // Gradient color blend from purple to orange
      const mixRatio = (Math.sin(theta) + 1) / 2;
      const color = purpleColor.clone().lerp(orangeColor, mixRatio);
      if (i % 7 === 0) color.lerp(cyanColor, 0.6);

      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // Particle Material
    const pMaterial = new THREE.PointsMaterial({
      size: 0.38,
      vertexColors: true,
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending,
    });

    const particles = new THREE.Points(geometry, pMaterial);
    scene.add(particles);

    // Wireframe Icosahedron Inner Core
    const innerGeo = new THREE.IcosahedronGeometry(7.5, 2);
    const innerMat = new THREE.MeshBasicMaterial({
      color: 0x8b5cf6,
      wireframe: true,
      transparent: true,
      opacity: 0.25,
    });
    const innerMesh = new THREE.Mesh(innerGeo, innerMat);
    scene.add(innerMesh);

    // Outer Floating Rings
    const ringGeo = new THREE.TorusGeometry(15.5, 0.08, 16, 100);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0xf97316,
      transparent: true,
      opacity: 0.35,
    });
    const ringMesh1 = new THREE.Mesh(ringGeo, ringMat);
    ringMesh1.rotation.x = Math.PI / 3;
    scene.add(ringMesh1);

    const ringMesh2 = new THREE.Mesh(ringGeo, new THREE.MeshBasicMaterial({
      color: 0xa855f7,
      transparent: true,
      opacity: 0.3,
    }));
    ringMesh2.rotation.y = Math.PI / 4;
    ringMesh2.rotation.x = -Math.PI / 6;
    scene.add(ringMesh2);

    // Mouse Tracking
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      targetX = (x / width - 0.5) * 2;
      targetY = -(y / height - 0.5) * 2;
    };

    window.addEventListener('mousemove', handleMouseMove);

    // Resize Handler
    const handleResize = () => {
      if (!containerRef.current) return;
      const newWidth = containerRef.current.clientWidth;
      const newHeight = containerRef.current.clientHeight;
      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
    };

    window.addEventListener('resize', handleResize);

    // Animation Loop
    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      // Smooth mouse interpolation
      mouseX += (targetX - mouseX) * 0.05;
      mouseY += (targetY - mouseY) * 0.05;

      particles.rotation.y = elapsedTime * 0.08 + mouseX * 0.4;
      particles.rotation.x = elapsedTime * 0.05 + mouseY * 0.3;

      innerMesh.rotation.y = -elapsedTime * 0.12;
      innerMesh.rotation.x = elapsedTime * 0.08;

      ringMesh1.rotation.z = elapsedTime * 0.15;
      ringMesh2.rotation.z = -elapsedTime * 0.1;

      // Gentle floating pulsation
      const scale = 1 + Math.sin(elapsedTime * 1.5) * 0.03;
      innerMesh.scale.set(scale, scale, scale);

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      geometry.dispose();
      pMaterial.dispose();
      innerGeo.dispose();
      innerMat.dispose();
      ringGeo.dispose();
      ringMat.dispose();
      renderer.dispose();
    };
  }, []);

  return (
    <div className="relative w-full h-[480px] lg:h-[600px] flex items-center justify-center overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute w-72 h-72 rounded-full bg-purple-600/20 blur-[90px] pointer-events-none -top-10 -left-10" />
      <div className="absolute w-72 h-72 rounded-full bg-orange-500/15 blur-[90px] pointer-events-none -bottom-10 -right-10" />
      
      {/* Three.js Canvas Container */}
      <div ref={containerRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

      {/* Floating telemetry pills */}
      <div className="absolute top-10 left-6 lg:left-12 glass-panel rounded-xl px-4 py-2.5 flex items-center gap-3 border border-purple-500/20 shadow-glow-purple backdrop-blur-md animate-pulse">
        <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
        <div>
          <div className="text-[11px] font-medium text-gray-400">Autonomous Nodes</div>
          <div className="text-xs font-bold text-white font-mono-numbers">1,800 Active Clusters</div>
        </div>
      </div>

      <div className="absolute bottom-12 right-6 lg:right-12 glass-panel rounded-xl px-4 py-2.5 flex items-center gap-3 border border-orange-500/20 shadow-glow-orange backdrop-blur-md">
        <div className="w-2.5 h-2.5 rounded-full bg-orange-400" />
        <div>
          <div className="text-[11px] font-medium text-gray-400">Neural Inference Speed</div>
          <div className="text-xs font-bold text-orange-300 font-mono-numbers">8.4ms Sub-Tick Latency</div>
        </div>
      </div>
    </div>
  );
};

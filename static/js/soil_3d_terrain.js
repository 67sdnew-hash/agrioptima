/**
 * AgriOptima - Interactive 3D Soil Digital Twin & Nutrient Field (Three.js)
 */

function initSoil3DField(containerId) {
  const container = document.getElementById(containerId);
  if (!container || typeof THREE === 'undefined') return;

  // Clear previous canvas if any
  container.innerHTML = '';

  const width = container.clientWidth || 600;
  const height = container.clientHeight || 280;

  // 1. Scene, Camera, Renderer
  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x0f172a, 0.025);

  const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
  camera.position.set(0, 18, 30);
  camera.lookAt(0, 0, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  // 2. Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0x10b981, 1.2);
  directionalLight.position.set(20, 30, 20);
  scene.add(directionalLight);

  const pointLightAmber = new THREE.PointLight(0xf59e0b, 1.5, 40);
  pointLightAmber.position.set(-15, 10, -10);
  scene.add(pointLightAmber);

  const pointLightCyan = new THREE.PointLight(0x06b6d4, 1.5, 40);
  pointLightCyan.position.set(15, 10, -10);
  scene.add(pointLightCyan);

  // 3. Undulating 3D Soil Mesh
  const gridWidth = 40;
  const gridHeight = 40;
  const segments = 45;
  const geometry = new THREE.PlaneGeometry(gridWidth, gridHeight, segments, segments);
  geometry.rotateX(-Math.PI / 2);

  // Material with soft sage/emerald wireframe & shaded surface
  const material = new THREE.MeshStandardMaterial({
    color: 0x334155,
    wireframe: true,
    roughness: 0.8,
    metalness: 0.2,
  });

  const soilMesh = new THREE.Mesh(geometry, material);
  scene.add(soilMesh);

  // 4. Floating Nutrient Ion Particles (N, P, K)
  const particleCount = 120;
  const particleGeometry = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);
  const colors = new Float32Array(particleCount * 3);

  const colorN = new THREE.Color(0x38bdf8); // Cyan for N
  const colorP = new THREE.Color(0xfbbf24); // Gold for P
  const colorK = new THREE.Color(0x34d399); // Emerald for K

  for (let i = 0; i < particleCount; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 36;
    positions[i * 3 + 1] = Math.random() * 12 + 1;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 36;

    let chosenColor = colorK;
    const r = Math.random();
    if (r < 0.33) chosenColor = colorN;
    else if (r < 0.66) chosenColor = colorP;

    colors[i * 3] = chosenColor.r;
    colors[i * 3 + 1] = chosenColor.g;
    colors[i * 3 + 2] = chosenColor.b;
  }

  particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  particleGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

  const particleMaterial = new THREE.PointsMaterial({
    size: 0.65,
    vertexColors: true,
    transparent: true,
    opacity: 0.85,
    blending: THREE.AdditiveBlending,
  });

  const particles = new THREE.Points(particleGeometry, particleMaterial);
  scene.add(particles);

  // 5. Cursor Touch Interaction Tracking
  let targetRotationX = 0;
  let targetRotationY = 0;

  function onPointerMove(clientX, clientY) {
    const rect = container.getBoundingClientRect();
    if (
      clientX >= rect.left &&
      clientX <= rect.right &&
      clientY >= rect.top &&
      clientY <= rect.bottom
    ) {
      const normX = ((clientX - rect.left) / rect.width) * 2 - 1;
      const normY = -(((clientY - rect.top) / rect.height) * 2 - 1);
      targetRotationY = normX * 0.45;
      targetRotationX = normY * 0.25;
    }
  }

  window.addEventListener('mousemove', (e) => onPointerMove(e.clientX, e.clientY));
  window.addEventListener('touchmove', (e) => {
    if (e.touches && e.touches[0]) {
      onPointerMove(e.touches[0].clientX, e.touches[0].clientY);
    }
  }, { passive: true });

  // 6. Animation Loop
  let clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);

    const elapsedTime = clock.getElapsedTime();

    // Terrain wave simulation
    const pos = geometry.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const u = pos.getX(i);
      const v = pos.getZ(i);
      const wave =
        Math.sin(u * 0.3 + elapsedTime * 1.2) * 1.1 +
        Math.cos(v * 0.35 + elapsedTime * 1.1) * 1.1;
      pos.setY(i, wave);
    }
    pos.needsUpdate = true;

    // Smooth cursor inertia tilt
    soilMesh.rotation.y += (targetRotationY - soilMesh.rotation.y) * 0.05;
    soilMesh.rotation.x = 0.15 + (targetRotationX - soilMesh.rotation.x) * 0.05;

    // Particle subtle float and rotation
    particles.rotation.y = elapsedTime * 0.05;
    const particlePositions = particleGeometry.attributes.position.array;
    for (let i = 0; i < particleCount; i++) {
      particlePositions[i * 3 + 1] += Math.sin(elapsedTime * 2 + i) * 0.015;
    }
    particleGeometry.attributes.position.needsUpdate = true;

    renderer.render(scene, camera);
  }
  animate();

  // Resize handler
  window.addEventListener('resize', () => {
    const newW = container.clientWidth || 600;
    const newH = container.clientHeight || 280;
    camera.aspect = newW / newH;
    camera.updateProjectionMatrix();
    renderer.setSize(newW, newH);
  });
}

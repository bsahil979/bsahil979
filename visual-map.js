/**
 * visual-map.js — Genuinely Live 60 FPS Biometric Developer Identity Scanner
 * Inspired by cybernetic terminal aesthetics & Dennis Snellenberg precision.
 * 
 * Architecture:
 * ├── VisualMapConfig
 * ├── ParticlePortrait (Real-time point-cloud physics & spring reformation)
 * ├── ScanLine (Laser sweep & particle activation)
 * ├── HudRings (Concentric rotating arcs & radar pulse waves)
 * ├── Waveform (Mathematical biometric wave equation)
 * ├── Telemetry (Live FPS calculation, slow-fluctuating match %, system status)
 * └── VisualMapRenderer (Main requestAnimationFrame coordinator)
 */

(function () {
  'use strict';

  // =========================================================================
  // 1. CONFIGURATION
  // =========================================================================
  const VisualMapConfig = {
    canvasWidth: 420,
    canvasHeight: 470,
    particleSize: 1.25,
    scanSpeed: 0.0018,          // Cycles per millisecond (~3.5s per sweep)
    scanHeight: 340,
    scanTop: 146,
    scanBottom: 486,
    springK: 0.075,              // Elastic spring constant for reformation
    damping: 0.84,               // Velocity friction damping
    mouseRadius: 75,             // Pointer disturbance radius
    mouseForce: 1.6,             // Pointer repulsion force
    waveformBaseY: 506,
    waveformAmp: 6.5,
    colors: {
      bg: '#0D1628',
      panel2: '#101B30',
      line: '#25344C',
      muted: '#8291A8',
      text: '#DDE7F5',
      portrait: '#AA9BEF',       // Primary lavender
      portraitGlow: '#C4B8FF',
      cyan: '#22D3EE',           // Laser & HUD cyan
      cyanGlow: 'rgba(34, 211, 238, 0.4)',
      accent: '#10B981',         // Terminal nominal emerald
      alert: '#FF4D5A',          // Live red
      radarRing: '#1F2F4A'
    }
  };

  // =========================================================================
  // 2. PARTICLE PORTRAIT SYSTEM
  // =========================================================================
  class ParticlePortrait {
    constructor(config) {
      this.cfg = config;
      this.particles = [];
      this.floatingDust = [];
      this.glitchActive = false;
      this.glitchY = 0;
      this.glitchHeight = 0;
      this.glitchOffset = 0;
      this.lastGlitchTime = 0;
      this.isLoaded = false;
      this.totalExtracted = 0;

      this.initFloatingDust();
    }

    initFloatingDust() {
      this.floatingDust = [];
      const dustCount = 45;
      for (let i = 0; i < dustCount; i++) {
        this.floatingDust.push({
          x: 40 + Math.random() * 340,
          y: 130 + Math.random() * 360,
          vx: (Math.random() - 0.5) * 0.35,
          vy: -0.15 - Math.random() * 0.25,
          size: 0.6 + Math.random() * 0.8,
          alpha: 0.15 + Math.random() * 0.35,
          phase: Math.random() * Math.PI * 2,
          color: Math.random() > 0.5 ? this.cfg.colors.cyan : this.cfg.colors.portrait
        });
      }
    }

    loadFromData(dataArray) {
      this.particles = [];
      const isMobile = window.innerWidth <= 768;
      const step = isMobile ? 2 : 1;

      for (let i = 0; i < dataArray.length; i += step) {
        const item = dataArray[i];
        // item: [x, y, brightness] (x in [0..300], y in [0..340])
        const targetX = 60 + item[0];
        const targetY = 146 + item[1];
        const brightness = item[2] || 0.5;

        // Base opacity scaled by facial luminance
        const baseAlpha = 0.35 + brightness * 0.6;
        const depth = 0.5 + Math.random() * 0.8;
        const baseSize = 0.95 + brightness * 0.5;

        this.particles.push({
          x: targetX + (Math.random() - 0.5) * 6,
          y: targetY + (Math.random() - 0.5) * 6,
          targetX: targetX,
          targetY: targetY,
          vx: 0,
          vy: 0,
          baseSize: baseSize,
          size: baseSize,
          baseAlpha: baseAlpha,
          alpha: baseAlpha,
          brightness: brightness,
          depth: depth,
          phase: Math.random() * Math.PI * 2,
          speed: 0.7 + Math.random() * 0.6,
          isCyan: Math.random() < 0.08
        });
      }

      this.totalExtracted = this.particles.length;
      this.isLoaded = true;
    }

    update(time, scanY, mouse) {
      // 1. Periodic Controlled Micro-Glitch (every 4.5 - 7 seconds for 120ms)
      if (time - this.lastGlitchTime > 5200 + (time % 2000)) {
        this.glitchActive = true;
        this.glitchY = 180 + Math.random() * 240;
        this.glitchHeight = 12 + Math.random() * 18;
        this.glitchOffset = (Math.random() > 0.5 ? 1 : -1) * (3.5 + Math.random() * 4.5);
        this.lastGlitchTime = time;
      } else if (this.glitchActive && time - this.lastGlitchTime > 130) {
        this.glitchActive = false;
        this.glitchOffset = 0;
      }

      const scanWidth = 26;
      const k = this.cfg.springK;
      const damping = this.cfg.damping;
      const mouseR = this.cfg.mouseRadius;
      const mouseForce = this.cfg.mouseForce;

      for (let i = 0; i < this.particles.length; i++) {
        const p = this.particles[i];

        // Particle Breathing
        const breathX = Math.sin(time * 0.0016 * p.speed + p.phase) * (0.75 * p.depth);
        const breathY = Math.cos(time * 0.0012 * p.speed + p.phase) * (0.65 * p.depth);

        let idealX = p.targetX + breathX;
        let idealY = p.targetY + breathY;

        // Apply Micro-Glitch slice
        if (this.glitchActive && p.targetY >= this.glitchY && p.targetY <= this.glitchY + this.glitchHeight) {
          idealX += this.glitchOffset;
          p.alpha = Math.min(1.0, p.alpha + 0.3);
        }

        // Scan Sweep Interaction
        const dyScan = p.y - scanY;
        if (Math.abs(dyScan) < scanWidth) {
          const scanFactor = 1 - Math.abs(dyScan) / scanWidth;
          p.alpha = Math.min(1.0, p.baseAlpha + scanFactor * 0.55);
          p.size = p.baseSize * (1 + scanFactor * 0.7);

          // Subtle outward laser pulse displacement
          const scatterAngle = p.phase;
          p.vx += Math.cos(scatterAngle) * scanFactor * 1.4;
          p.vy += (dyScan >= 0 ? 1 : -1) * scanFactor * 1.8;
        }

        // Mouse Repulsion & Illumination
        if (mouse.active) {
          const mdx = p.x - mouse.x;
          const mdy = p.y - mouse.y;
          const mDist = Math.hypot(mdx, mdy);
          if (mDist < mouseR && mDist > 0) {
            const force = (1 - mDist / mouseR) * mouseForce;
            p.vx += (mdx / mDist) * force * 1.1;
            p.vy += (mdy / mDist) * force * 1.1;
            p.alpha = Math.min(1.0, p.alpha + force * 0.45);
            p.size = Math.max(p.size, p.baseSize * (1 + force * 0.4));
          }
        }

        // Damped Spring Physics toward Rest Target
        const ax = (idealX - p.x) * k;
        const ay = (idealY - p.y) * k;
        p.vx = (p.vx + ax) * damping;
        p.vy = (p.vy + ay) * damping;
        p.x += p.vx;
        p.y += p.vy;

        // Smooth restitution of scale & opacity
        p.size += (p.baseSize - p.size) * 0.08;
        p.alpha += (p.baseAlpha - p.alpha) * 0.08;
      }

      // Update ambient floating dust
      for (let i = 0; i < this.floatingDust.length; i++) {
        const d = this.floatingDust[i];
        d.x += d.vx + Math.sin(time * 0.001 + d.phase) * 0.2;
        d.y += d.vy;
        if (d.y < 125) {
          d.y = 485;
          d.x = 40 + Math.random() * 340;
        }
      }
    }

    draw(ctx, scanY) {
      if (!this.isLoaded) return;

      const colors = this.cfg.colors;

      // 1. Draw ambient floating dust
      for (let i = 0; i < this.floatingDust.length; i++) {
        const d = this.floatingDust[i];
        ctx.fillStyle = d.color;
        ctx.globalAlpha = d.alpha;
        ctx.beginPath();
        ctx.arc(d.x, d.y, d.size, 0, Math.PI * 2);
        ctx.fill();
      }

      // 2. Draw portrait particles
      const scanWidth = 26;
      for (let i = 0; i < this.particles.length; i++) {
        const p = this.particles[i];
        const nearScan = Math.abs(p.y - scanY) < scanWidth;

        // Near the laser scan line, particles become vibrant cyan
        if (nearScan) {
          ctx.fillStyle = colors.cyan;
        } else if (p.isCyan) {
          ctx.fillStyle = colors.cyan;
        } else {
          ctx.fillStyle = colors.portrait;
        }

        ctx.globalAlpha = p.alpha;
        const half = p.size * 0.5;
        ctx.fillRect(p.x - half, p.y - half, p.size, p.size);
      }

      ctx.globalAlpha = 1.0;
    }
  }

  // =========================================================================
  // 3. SCAN LINE & LASER EFFECT
  // =========================================================================
  class ScanLine {
    constructor(config) {
      this.cfg = config;
      this.y = config.scanTop;
    }

    update(time) {
      const top = this.cfg.scanTop;
      const bottom = this.cfg.scanBottom;
      const range = bottom - top;
      // Triangle wave oscillating top to bottom
      const progress = ((time * this.cfg.scanSpeed) % 2);
      if (progress <= 1) {
        this.y = top + progress * range;
      } else {
        this.y = bottom - (progress - 1) * range;
      }
    }

    draw(ctx) {
      const colors = this.cfg.colors;
      const x1 = 50;
      const x2 = 370;
      const y = this.y;

      ctx.save();

      // Outer laser aura
      const grad = ctx.createLinearGradient(0, y - 18, 0, y + 18);
      grad.addColorStop(0, 'rgba(34, 211, 238, 0)');
      grad.addColorStop(0.5, 'rgba(34, 211, 238, 0.22)');
      grad.addColorStop(1, 'rgba(34, 211, 238, 0)');
      ctx.fillStyle = grad;
      ctx.fillRect(x1, y - 18, x2 - x1, 36);

      // Core sharp laser beam
      ctx.strokeStyle = colors.cyan;
      ctx.lineWidth = 1.4;
      ctx.shadowColor = colors.cyan;
      ctx.shadowBlur = 8;
      ctx.beginPath();
      ctx.moveTo(x1, y);
      ctx.lineTo(x2, y);
      ctx.stroke();

      // Laser endpoint diamonds
      ctx.fillStyle = colors.cyan;
      ctx.fillRect(x1 - 3, y - 3, 6, 6);
      ctx.fillRect(x2 - 3, y - 3, 6, 6);

      ctx.restore();
    }
  }

  // =========================================================================
  // 4. CONCENTRIC HUD RINGS & RADAR PULSES
  // =========================================================================
  class HudRings {
    constructor(config) {
      this.cfg = config;
      this.cx = 210;   // Centered horizontally over portrait
      this.cy = 300;   // Centered over facial features
      this.pulseR = 25;
      this.pulseAlpha = 0.7;
    }

    update(time) {
      // Expanding radar pulse wave (cycles every 3.4 seconds)
      const tPulse = (time % 3400) / 3400;
      this.pulseR = 25 + tPulse * 155;
      this.pulseAlpha = 0.75 * (1 - tPulse);
    }

    draw(ctx, time) {
      const colors = this.cfg.colors;
      const cx = this.cx;
      const cy = this.cy;

      ctx.save();

      // 1. Cross coordinate grid lines
      ctx.strokeStyle = colors.line;
      ctx.lineWidth = 1;
      ctx.setLineDash([2, 6]);
      ctx.globalAlpha = 0.45;
      ctx.beginPath();
      ctx.moveTo(cx, 130);
      ctx.lineTo(cx, 495);
      ctx.moveTo(40, cy);
      ctx.lineTo(380, cy);
      ctx.stroke();
      ctx.setLineDash([]);

      // 2. Static faint radar concentric guides
      ctx.strokeStyle = colors.radarRing;
      ctx.lineWidth = 1;
      ctx.globalAlpha = 0.35;
      ctx.beginPath();
      ctx.arc(cx, cy, 70, 0, Math.PI * 2);
      ctx.arc(cx, cy, 125, 0, Math.PI * 2);
      ctx.stroke();

      // 3. Rotating Inner Segmented Ring (CW)
      const rotCW = time * 0.00045;
      ctx.strokeStyle = colors.cyan;
      ctx.lineWidth = 1.2;
      ctx.globalAlpha = 0.55;
      ctx.beginPath();
      for (let i = 0; i < 4; i++) {
        const start = rotCW + (i * Math.PI) / 2;
        ctx.arc(cx, cy, 60, start, start + 0.35);
      }
      ctx.stroke();

      // 4. Rotating Outer Segmented Arc Ring (CCW)
      const rotCCW = -time * 0.00035;
      ctx.strokeStyle = colors.portrait;
      ctx.lineWidth = 1.2;
      ctx.globalAlpha = 0.65;
      ctx.beginPath();
      for (let i = 0; i < 3; i++) {
        const start = rotCCW + (i * Math.PI * 2) / 3;
        ctx.arc(cx, cy, 140, start, start + 0.55);
      }
      ctx.stroke();

      // 5. Dynamic Expanding Radar Pulse Wave
      ctx.strokeStyle = colors.cyan;
      ctx.lineWidth = 1.2;
      ctx.globalAlpha = this.pulseAlpha;
      ctx.beginPath();
      ctx.arc(cx, cy, this.pulseR, 0, Math.PI * 2);
      ctx.stroke();

      // Dual secondary pulse (phase offset)
      const p2 = ((time + 1700) % 3400) / 3400;
      ctx.strokeStyle = colors.portrait;
      ctx.globalAlpha = 0.75 * (1 - p2);
      ctx.beginPath();
      ctx.arc(cx, cy, 25 + p2 * 155, 0, Math.PI * 2);
      ctx.stroke();

      ctx.restore();
    }
  }

  // =========================================================================
  // 5. BIOMETRIC MATHEMATICAL WAVEFORM
  // =========================================================================
  class Waveform {
    constructor(config) {
      this.cfg = config;
    }

    draw(ctx, time) {
      const colors = this.cfg.colors;
      const baseY = this.cfg.waveformBaseY;
      const startX = 45;
      const endX = 375;
      const width = endX - startX;

      ctx.save();

      // Wave path formula: envelope * combined sines + heartbeat pulse
      ctx.beginPath();
      let first = true;

      for (let x = startX; x <= endX; x += 3) {
        const norm = (x - startX) / width;
        const envelope = Math.sin(norm * Math.PI); // Window function: 0 at edges, 1 at center

        const w1 = Math.sin(x * 0.045 + time * 0.0035) * 4.5;
        const w2 = Math.sin(x * 0.082 - time * 0.0055) * 2.8;
        const w3 = Math.cos(x * 0.024 + time * 0.0018) * 2.2;

        // Biometric QRS cardiac heartbeat pulse traveling across waveform
        const pulsePos = ((time * 0.00045) % 1.0);
        let cardiac = 0;
        const distToPulse = Math.abs(norm - pulsePos);
        if (distToPulse < 0.07) {
          cardiac = Math.sin((norm - pulsePos) / 0.07 * Math.PI) * 9.5;
        }

        const y = baseY + (w1 + w2 + w3 + cardiac) * envelope;

        if (first) {
          ctx.moveTo(x, y);
          first = false;
        } else {
          ctx.lineTo(x, y);
        }
      }

      ctx.strokeStyle = colors.portrait;
      ctx.lineWidth = 1.4;
      ctx.globalAlpha = 0.65;
      ctx.stroke();

      // Ambient baseline
      ctx.strokeStyle = colors.line;
      ctx.lineWidth = 0.8;
      ctx.globalAlpha = 0.35;
      ctx.beginPath();
      ctx.moveTo(startX, baseY);
      ctx.lineTo(endX, baseY);
      ctx.stroke();

      ctx.restore();
    }
  }

  // =========================================================================
  // 6. LIVE TELEMETRY & HUD SYSTEM
  // =========================================================================
  class Telemetry {
    constructor(config) {
      this.cfg = config;
      this.fps = 60;
      this.frameCount = 0;
      this.lastFpsUpdate = 0;
      this.matchPercent = '99.8%';
      this.lastMatchTime = 0;
    }

    update(time) {
      // Calculate true FPS every 500ms
      this.frameCount++;
      if (time - this.lastFpsUpdate > 500) {
        this.fps = Math.round((this.frameCount * 1000) / (time - this.lastFpsUpdate));
        this.frameCount = 0;
        this.lastFpsUpdate = time;
      }

      // Smoothly fluctuate identity match percentage between 99.6% and 99.9%
      if (time - this.lastMatchTime > 1800) {
        const val = (99.75 + Math.sin(time * 0.0007) * 0.12 + Math.cos(time * 0.0003) * 0.06).toFixed(1);
        this.matchPercent = `${val}%`;
        this.lastMatchTime = time;
      }
    }

    draw(ctx, particleCount, time) {
      const colors = this.cfg.colors;
      ctx.save();

      // Top Header: VISUAL.MAP + Resolution
      ctx.font = '700 13px ui-monospace, SFMono-Regular, Consolas, monospace';
      ctx.fillStyle = colors.cyan;
      ctx.fillText('VISUAL.MAP', 50, 111);

      ctx.font = '11px ui-monospace, SFMono-Regular, Consolas, monospace';
      ctx.fillStyle = colors.muted;
      ctx.textAlign = 'right';
      ctx.fillText('300×340 / 1-BIT', 370, 111);

      // Top Right Telemetry Indicators
      ctx.font = '600 10px ui-monospace, SFMono-Regular, Consolas, monospace';
      ctx.fillStyle = colors.accent;
      ctx.fillText(`SCAN: ACTIVE`, 370, 138);

      ctx.fillStyle = colors.cyan;
      ctx.fillText(`FPS: ${this.fps}`, 370, 152);

      // Facial Target Reticle Brackets
      const rx = 120, ry = 172, rw = 180, rh = 220;
      ctx.strokeStyle = colors.cyan;
      ctx.lineWidth = 1.2;
      ctx.globalAlpha = 0.65;
      ctx.beginPath();
      // Corners
      ctx.moveTo(rx, ry + 12); ctx.lineTo(rx, ry); ctx.lineTo(rx + 12, ry);
      ctx.moveTo(rx + rw - 12, ry); ctx.lineTo(rx + rw, ry); ctx.lineTo(rx + rw, ry + 12);
      ctx.moveTo(rx, ry + rh - 12); ctx.lineTo(rx, ry + rh); ctx.lineTo(rx + 12, ry + rh);
      ctx.moveTo(rx + rw - 12, ry + rh); ctx.lineTo(rx + rw, ry + rh); ctx.lineTo(rx + rw, ry + rh - 12);
      ctx.stroke();

      // Target Label
      ctx.font = '700 9px ui-monospace, SFMono-Regular, Consolas, monospace';
      ctx.fillStyle = colors.cyan;
      ctx.textAlign = 'left';
      ctx.fillText('ID: SAHIL_BELCHADA', rx + 4, ry - 7);

      ctx.fillStyle = colors.accent;
      ctx.textAlign = 'right';
      ctx.fillText(`MATCH: ${this.matchPercent}`, rx + rw - 4, ry - 7);

      // Bottom Telemetry Stats
      ctx.font = '10px ui-monospace, SFMono-Regular, Consolas, monospace';
      ctx.fillStyle = colors.muted;
      ctx.textAlign = 'left';
      const ptsStr = String(particleCount || 14594).padStart(6, '0');
      ctx.fillText(`PTS ${ptsStr} · FS/SERPENTINE · SYS_NOMINAL`, 50, 538);

      ctx.restore();
    }
  }

  // =========================================================================
  // 7. VISUAL MAP MAIN ENGINE & RENDERER
  // =========================================================================
  class VisualMapRenderer {
    constructor(canvasElement) {
      this.canvas = canvasElement;
      this.ctx = canvasElement.getContext('2d');
      this.cfg = VisualMapConfig;

      this.portrait = new ParticlePortrait(this.cfg);
      this.scanLine = new ScanLine(this.cfg);
      this.hudRings = new HudRings(this.cfg);
      this.waveform = new Waveform(this.cfg);
      this.telemetry = new Telemetry(this.cfg);

      this.mouse = { x: -999, y: -999, active: false };
      this.animId = null;
      this.scaleFactor = 1;

      this.initEvents();
      this.setupCanvas();
      this.loadParticles();
    }

    setupCanvas() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const displayW = this.canvas.clientWidth || this.cfg.canvasWidth;
      const displayH = this.canvas.clientHeight || this.cfg.canvasHeight;

      this.canvas.width = displayW * dpr;
      this.canvas.height = displayH * dpr;
      this.ctx.scale(dpr, dpr);

      // Coordinate scaling factor for responsive bounds
      this.scaleFactor = displayW / this.cfg.canvasWidth;
    }

    initEvents() {
      const updateMouse = (clientX, clientY) => {
        const rect = this.canvas.getBoundingClientRect();
        this.mouse.x = (clientX - rect.left);
        this.mouse.y = (clientY - rect.top);
        this.mouse.active = true;
      };

      this.canvas.addEventListener('mousemove', (e) => {
        updateMouse(e.clientX, e.clientY);
      });

      this.canvas.addEventListener('mouseleave', () => {
        this.mouse.active = false;
        this.mouse.x = -999;
        this.mouse.y = -999;
      });

      this.canvas.addEventListener('touchmove', (e) => {
        if (e.touches.length > 0) {
          updateMouse(e.touches[0].clientX, e.touches[0].clientY);
        }
      }, { passive: true });

      this.canvas.addEventListener('touchend', () => {
        this.mouse.active = false;
      });

      window.addEventListener('resize', () => {
        this.setupCanvas();
      });
    }

    loadParticles() {
      // 1. If pre-computed particle dataset is loaded globally, use immediately
      if (window.SAHIL_PORTRAIT_PARTICLES && Array.isArray(window.SAHIL_PORTRAIT_PARTICLES)) {
        this.portrait.loadFromData(window.SAHIL_PORTRAIT_PARTICLES);
        return;
      }

      // 2. Otherwise load directly from sahil.jpg using offscreen canvas analysis
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.src = 'assets/sahil.jpg';
      img.onload = () => {
        const offCanvas = document.createElement('canvas');
        const offCtx = offCanvas.getContext('2d');
        const targetW = 300, targetH = 340;
        offCanvas.width = targetW;
        offCanvas.height = targetH;

        // Crop centered face:
        const cropW = img.width * 0.8;
        const cropH = cropW * (targetH / targetW);
        const cropX = (img.width - cropW) / 2;
        const cropY = img.height * 0.08;

        offCtx.drawImage(img, cropX, cropY, cropW, cropH, 0, 0, targetW, targetH);
        const imgData = offCtx.getImageData(0, 0, targetW, targetH).data;

        const points = [];
        for (let y = 0; y < targetH; y += 2) {
          for (let x = 0; x < targetW; x += 2) {
            const idx = (y * targetW + x) * 4;
            const r = imgData[idx];
            const g = imgData[idx + 1];
            const b = imgData[idx + 2];
            const lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

            // Reject off-white studio background (bright neutral)
            const isStudioBg = (r > 215 && g > 215 && b > 215 && Math.abs(r - b) < 18);
            if (!isStudioBg) {
              points.push([x, y, lum]);
            }
          }
        }
        this.portrait.loadFromData(points);
      };

      img.onerror = () => {
        console.warn('Direct image load fallback initiated.');
      };
    }

    render(time) {
      const ctx = this.ctx;
      const colors = this.cfg.colors;
      const w = this.canvas.clientWidth || this.cfg.canvasWidth;
      const h = this.canvas.clientHeight || this.cfg.canvasHeight;

      // Clear Canvas
      ctx.clearRect(0, 0, w, h);

      // Terminal Panel Background & Border
      ctx.fillStyle = colors.panel2;
      ctx.strokeStyle = colors.line;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(16, 16, w - 32, h - 32, 8);
      ctx.fill();
      ctx.stroke();

      // Header separator
      ctx.beginPath();
      ctx.moveTo(16, 124);
      ctx.lineTo(w - 16, 124);
      ctx.stroke();

      // Corner technical brackets
      ctx.strokeStyle = colors.cyan;
      ctx.lineWidth = 1;
      ctx.globalAlpha = 0.55;
      ctx.beginPath();
      ctx.moveTo(31, 141); ctx.lineTo(43, 141);
      ctx.moveTo(31, 141); ctx.lineTo(31, 153);
      ctx.moveTo(w - 31, 141); ctx.lineTo(w - 43, 141);
      ctx.moveTo(w - 31, 141); ctx.lineTo(w - 31, 153);
      ctx.moveTo(31, h - 31); ctx.lineTo(43, h - 31);
      ctx.moveTo(31, h - 31); ctx.lineTo(31, h - 43);
      ctx.moveTo(w - 31, h - 31); ctx.lineTo(w - 43, h - 31);
      ctx.moveTo(w - 31, h - 31); ctx.lineTo(w - 31, h - 43);
      ctx.stroke();
      ctx.globalAlpha = 1.0;

      // Update Systems
      this.scanLine.update(time);
      this.hudRings.update(time);
      this.telemetry.update(time);
      this.portrait.update(time, this.scanLine.y, this.mouse);

      // Draw Layers
      this.hudRings.draw(ctx, time);
      this.portrait.draw(ctx, this.scanLine.y);
      this.scanLine.draw(ctx);
      this.waveform.draw(ctx, time);
      this.telemetry.draw(ctx, this.portrait.totalExtracted, time);

      // Loop
      this.animId = requestAnimationFrame((t) => this.render(t));
    }

    start() {
      if (!this.animId) {
        this.animId = requestAnimationFrame((t) => this.render(t));
      }
    }

    stop() {
      if (this.animId) {
        cancelAnimationFrame(this.animId);
        this.animId = null;
      }
    }
  }

  // Expose globally
  window.VisualMapRenderer = VisualMapRenderer;

  // Auto-initialize if canvas element with id="visualMapCanvas" exists
  document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('visualMapCanvas');
    if (canvas) {
      const renderer = new VisualMapRenderer(canvas);
      renderer.start();
      window.activeVisualMap = renderer;
    }
  });

})();

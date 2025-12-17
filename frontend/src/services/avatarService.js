/**
 * Avatar Service for managing AI interviewer avatar
 */
export class AvatarService {
  constructor() {
    this.avatarElement = null;
    this.isAnimating = false;
    this.currentAudio = null;
    this.audioContext = null;
    this.analyser = null;
    this.dataArray = null;
    this.animationFrame = null;
  }

  /**
   * Initialize avatar with DOM element
   * @param {HTMLElement} avatarElement - Avatar DOM element
   */
  initialize(avatarElement) {
    this.avatarElement = avatarElement;
    this.setupAudioContext();
    this.createAvatarVisuals();
  }

  /**
   * Setup Web Audio API context for real-time audio analysis
   */
  setupAudioContext() {
    try {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
    } catch (error) {
      console.warn('Web Audio API not supported, using fallback animation');
    }
  }

// Replace the existing createAvatarVisuals function with this one

  /**
   * Create avatar visual elements and return the container
   * @returns {HTMLElement | null} The created avatar container element or null
   */
  createAvatarVisuals() {
    // 1. Create the main container element dynamically
    const container = document.createElement('div');
    container.className = 'avatar-interviewer'; // Add base class

    // 2. Set its inner HTML
    container.innerHTML = `
      <div class="avatar-container">
        <div class="avatar-head">
          <div class="avatar-face">
            <div class="avatar-eyes">
              <div class="avatar-eye left"><div class="pupil"></div><div class="eyelid"></div></div>
              <div class="avatar-eye right"><div class="pupil"></div><div class="eyelid"></div></div>
            </div>
            <div class="avatar-nose"></div>
            <div class="avatar-mouth">
              <div class="avatar-lips">
                <div class="upper-lip"></div>
                <div class="lower-lip"></div>
                <div class="mouth-opening"></div>
              </div>
            </div>
            <div class="avatar-cheeks">
              <div class="cheek left"></div>
              <div class="cheek right"></div>
            </div>
          </div>
          <div class="avatar-hair"></div>
        </div>
        <div class="avatar-body">
          <div class="avatar-torso"></div>
          <div class="avatar-arms">
            <div class="arm left"></div>
            <div class="arm right"></div>
          </div>
        </div>
      </div>
    `;

    // 3. Ensure styles are added (can be called separately if needed)
    this.addAvatarStyles(); 
    
    // 4. Return the created container element
    return container; 
  }

  /**
   * Add CSS styles for the avatar
   */
  addAvatarStyles() {
    if (document.getElementById('avatar-styles')) return;

    const style = document.createElement('style');
    style.id = 'avatar-styles';
    style.textContent = `
      .avatar-interviewer {
        position: relative;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
      }

      .avatar-container {
        position: relative;
        width: 200px;
        height: 250px;
        transform-style: preserve-3d;
        animation: float 3s ease-in-out infinite;
      }

      @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
      }

      .avatar-head {
        position: relative;
        width: 120px;
        height: 120px;
        background: #fdbcb4;
        border-radius: 50%;
        margin: 0 auto 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        transform-style: preserve-3d;
      }

      .avatar-face {
        position: relative;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        overflow: hidden;
      }

      .avatar-eyes {
        position: absolute;
        top: 30px;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        gap: 20px;
      }

      .avatar-eye {
        position: relative;
        width: 20px;
        height: 20px;
        background: white;
        border-radius: 50%;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
      }

      .pupil {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 12px;
        height: 12px;
        background: #333;
        border-radius: 50%;
        transition: all 0.1s ease;
      }

      .eyelid {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 50%;
        background: #fdbcb4;
        border-radius: 50% 50% 0 0;
        transition: transform 0.1s ease;
      }

      .avatar-nose {
        position: absolute;
        top: 50px;
        left: 50%;
        transform: translateX(-50%);
        width: 8px;
        height: 12px;
        background: #f4a5a5;
        border-radius: 50%;
      }

      .avatar-mouth {
        position: absolute;
        top: 70px;
        left: 50%;
        transform: translateX(-50%);
        width: 40px;
        height: 20px;
      }

      .avatar-lips {
        position: relative;
        width: 100%;
        height: 100%;
      }

      .upper-lip, .lower-lip {
        position: absolute;
        width: 100%;
        height: 50%;
        background: #d63384;
        border-radius: 50%;
        transition: all 0.1s ease;
      }

      .upper-lip {
        top: 0;
        border-radius: 50% 50% 0 0;
      }

      .lower-lip {
        bottom: 0;
        border-radius: 0 0 50% 50%;
      }

      .mouth-opening {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 20px;
        height: 8px;
        background: #000;
        border-radius: 50%;
        opacity: 0;
        transition: all 0.1s ease;
      }

      .avatar-cheeks {
        position: absolute;
        top: 50px;
        left: 0;
        right: 0;
        height: 30px;
      }

      .cheek {
        position: absolute;
        top: 0;
        width: 20px;
        height: 20px;
        background: #ffb3ba;
        border-radius: 50%;
        opacity: 0;
        transition: opacity 0.3s ease;
      }

      .cheek.left {
        left: 10px;
      }

      .cheek.right {
        right: 10px;
      }

      .avatar-hair {
        position: absolute;
        top: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 40px;
        background: #8b4513;
        border-radius: 50% 50% 0 0;
        z-index: -1;
      }

      .avatar-body {
        position: relative;
        width: 80px;
        height: 100px;
        background: #4a90e2;
        border-radius: 20px;
        margin: 0 auto;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
      }

      .avatar-torso {
        width: 100%;
        height: 60px;
        background: #4a90e2;
        border-radius: 20px 20px 10px 10px;
      }

      .avatar-arms {
        position: absolute;
        top: 10px;
        left: 0;
        right: 0;
        height: 40px;
      }

      .arm {
        position: absolute;
        width: 15px;
        height: 40px;
        background: #fdbcb4;
        border-radius: 10px;
      }

      .arm.left {
        left: -10px;
        top: 10px;
        transform: rotate(-20deg);
      }

      .arm.right {
        right: -10px;
        top: 10px;
        transform: rotate(20deg);
      }

      /* Expression styles */
      .expression-happy .avatar-eyes {
        transform: translateX(-50%) scaleY(0.8);
      }

      .expression-happy .avatar-lips {
        transform: scaleY(1.2);
      }

      .expression-happy .cheek {
        opacity: 1;
      }

      .expression-serious .avatar-eyes {
        transform: translateX(-50%) scaleY(1.2);
      }

      .expression-serious .avatar-lips {
        transform: scaleY(0.8);
      }

      .expression-thinking .avatar-eyes {
        transform: translateX(-50%) scaleY(0.6);
      }

      .expression-thinking .avatar-lips {
        transform: scaleY(0.9);
      }

      /* Speaking animation */
      .speaking .mouth-opening {
        opacity: 1;
        animation: mouth-move 0.1s ease-in-out infinite alternate;
      }

      @keyframes mouth-move {
        0% { transform: translate(-50%, -50%) scaleY(1); }
        100% { transform: translate(-50%, -50%) scaleY(1.5); }
      }

      /* Blinking animation */
      .avatar-eye .eyelid {
        animation: blink 4s infinite;
      }

      @keyframes blink {
        0%, 90%, 100% { transform: scaleY(1); }
        95% { transform: scaleY(0.1); }
      }
    `;
    
    document.head.appendChild(style);
  }

  /**
   * Start speaking animation with audio
   * @param {Blob} audioBlob - Audio blob to play
   * @param {string} text - Text being spoken (for fallback)
   */
  async startSpeaking(audioBlob, text = '') {
    if (this.isAnimating) {
      await this.stopSpeaking();
    }

    this.isAnimating = true;
    
    // Add speaking class for CSS animations
    if (this.avatarElement) {
      this.avatarElement.classList.add('speaking');
    }
    
    try {
      if (this.audioContext && audioBlob) {
        await this.playAudioWithLipSync(audioBlob);
      } else {
        // Fallback: animate based on text length
        this.animateWithText(text);
      }
    } catch (error) {
      console.error('Failed to start speaking animation:', error);
      // Fallback animation
      this.animateWithText(text);
    }
  }

  /**
   * Play audio with real-time lip sync
   * @param {Blob} audioBlob - Audio to play
   */
  async playAudioWithLipSync(audioBlob) {
    try {
      const arrayBuffer = await audioBlob.arrayBuffer();
      const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
      
      const source = this.audioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(this.analyser);
      this.analyser.connect(this.audioContext.destination);
      
      this.currentAudio = source;
      
      // Start lip sync animation
      this.startLipSyncAnimation();
      
      // Play audio
      source.start(0);
      
      // Stop animation when audio ends
      source.onended = () => {
        this.stopSpeaking();
      };
      
    } catch (error) {
      console.error('Audio playback failed:', error);
      throw error;
    }
  }

  /**
   * Start lip sync animation based on audio frequency
   */
  startLipSyncAnimation() {
    const animate = () => {
      if (!this.isAnimating) return;
      
      this.analyser.getByteFrequencyData(this.dataArray);
      
      // Calculate more sophisticated audio analysis
      const average = this.dataArray.reduce((a, b) => a + b) / this.dataArray.length;
      const max = Math.max(...this.dataArray);
      const min = Math.min(...this.dataArray);
      
      // Normalize to 0-1 with better scaling
      const normalized = Math.min(1, (average + (max - min) * 0.3) / 255);
      
      // Apply mouth animation with more realistic movement
      this.animateMouth(normalized);
      
      this.animationFrame = requestAnimationFrame(animate);
    };
    
    animate();
  }

  /**
   * Animate mouth based on audio intensity
   * @param {number} intensity - Audio intensity (0-1)
   */
  animateMouth(intensity) {
    const lips = this.avatarElement?.querySelector('.avatar-lips');
    const mouthOpening = this.avatarElement?.querySelector('.mouth-opening');
    if (!lips || !mouthOpening) return;
    
    // More realistic mouth movement
    const scale = 1 + (intensity * 0.8);
    const mouthScale = 0.5 + (intensity * 1.5);
    
    // Animate lips
    lips.style.transform = `scaleY(${scale})`;
    
    // Animate mouth opening
    mouthOpening.style.transform = `translate(-50%, -50%) scaleY(${mouthScale})`;
    mouthOpening.style.opacity = Math.min(1, intensity * 2);
    
    // Add some randomness for natural movement
    const randomOffset = (Math.random() - 0.5) * 0.2;
    lips.style.transform += ` translateY(${randomOffset}px)`;
  }

  /**
   * Fallback animation based on text length
   * @param {string} text - Text to animate for
   */
  animateWithText(text) {
    const duration = Math.max(text.length * 100, 2000); // 100ms per character, min 2s
    
    this.animateMouth(0.5); // Medium intensity
    
    setTimeout(() => {
      this.stopSpeaking();
    }, duration);
  }

  /**
   * Stop speaking animation
   */
  async stopSpeaking() {
    this.isAnimating = false;
    
    // Remove speaking class
    if (this.avatarElement) {
      this.avatarElement.classList.remove('speaking');
    }
    
    if (this.currentAudio) {
      this.currentAudio.stop();
      this.currentAudio = null;
    }
    
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
      this.animationFrame = null;
    }
    
    // Reset mouth to neutral position
    const lips = this.avatarElement?.querySelector('.avatar-lips');
    if (lips) {
      lips.style.transform = 'scaleY(1) translateY(0px)';
    }
  }

  /**
   * Set avatar expression
   * @param {string} expression - Expression type (happy, serious, thinking, etc.)
   */
  setExpression(expression) {
    if (!this.avatarElement) return;
    
    // Remove previous expression classes
    this.avatarElement.classList.remove('expression-happy', 'expression-serious', 'expression-thinking');
    
    // Add new expression class
    this.avatarElement.classList.add(`expression-${expression}`);
    
    // Update visual elements based on expression
    this.updateExpressionVisuals(expression);
  }

  /**
   * Update visual elements for expression
   * @param {string} expression - Expression type
   */
  updateExpressionVisuals(expression) {
    const eyes = this.avatarElement?.querySelector('.avatar-eyes');
    const mouth = this.avatarElement?.querySelector('.avatar-mouth');
    
    if (!eyes || !mouth) return;
    
    switch (expression) {
      case 'happy':
        eyes.style.transform = 'scaleY(0.8)';
        mouth.style.transform = 'scaleY(1.2)';
        break;
      case 'serious':
        eyes.style.transform = 'scaleY(1.2)';
        mouth.style.transform = 'scaleY(0.8)';
        break;
      case 'thinking':
        eyes.style.transform = 'scaleY(0.6)';
        mouth.style.transform = 'scaleY(0.9)';
        break;
      default:
        eyes.style.transform = 'scaleY(1)';
        mouth.style.transform = 'scaleY(1)';
    }
  }

  /**
   * Cleanup resources
   */
  destroy() {
    this.stopSpeaking();
    
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    
    this.avatarElement = null;
  }
}

// Global instance
export const avatarService = new AvatarService();



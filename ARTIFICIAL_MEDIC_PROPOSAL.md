# Proposal: Building the First Humanoid Artificial Medic

This document outlines the hardware selection and technical architecture for developing an autonomous medical humanoid capable of clinical decision-making and protocol execution using the Unitree G1 platform.

## 1. Hardware Selection: Recommended & Alternatives

To create a functional "Artificial Medic," we have evaluated several humanoid platforms. While the Unitree G1 EDU U4 remains our primary recommendation for versatility and cost-efficiency, other models offer specialized advantages.

### Primary Choice: Unitree G1 EDU Ultimate B (U4)
*   **Tactile Dexterity:** Features dual **Dex3-1 force-controlled dexterous hands** with tactile sensors. Essential for handling medical instruments or interacting with patients.
*   **Agility (43 DOF):** Maximum degrees of freedom in the G1 series for navigating clinical spaces.
*   **Compute:** **NVIDIA Jetson Orin (100 TOPS)** for local AI inference.
*   **Best for:** Research-focused prototypes and highly agile, small-scale medical assistants.

### Alternative A: Fourier GR-1 (Medical & Rehab Focus)
*   **Strengths:** Specifically marketed for "Medical and Rehab" scenarios. It is taller (165cm) and more powerful (230N·m peak torque), making it better suited for physically assisting patients (e.g., helping someone stand up).
*   **Compute:** Uses an **Intel i7-13700H** platform, which may be more familiar for standard software development but less optimized for edge-AI than the Jetson Orin.
*   **Best for:** Rehabilitation, patient transfer assistance, and clinical environments requiring a full-height presence.

### Alternative B: AgiBot A2 Ultra (Industrial Power)
*   **Strengths:** Features a more powerful **NVIDIA Jetson AGX Orin (64GB)** and 40 DOF. It is designed for high reliability and commercial-scale deployment.
*   **Dexterity:** Includes dual 6-DOF dexterous hands and a comprehensive multi-sensor array (LiDAR, dual RGBD, fisheye).
*   **Best for:** Large-scale commercial hospital deployments where high-uptime and superior compute are required for complex multi-modal AI.

---

## 2. Embedding Medical Knowledge: The "Artificial Medic" Brain

To make the robot "standalone" and capable of autonomous decision-making based on clinical protocols, we recommend a three-layer software architecture.

### Layer A: The Knowledge Base (Local RAG System)
Instead of just training a model once, you should use **Retrieval-Augmented Generation (RAG)**.
*   **Data Injection:** Upload PDFs, manuals, and Paramedic protocols into a local vector database (e.g., **ChromaDB** or **FAISS**) running on the Jetson Orin.
*   **Retrieval:** When the robot encounters a situation (e.g., "Patient has a heavy bleed"), the system queries the vector database for the specific protocol.
*   **Decision:** A local LLM (e.g., **Llama 3-8B** or **Phi-3**, quantized for Jetson) processes the retrieved protocol and the current sensor data to decide the next action.

### Layer B: Perception & Vision
The robot must see and understand the patient.
*   **Visual Recognition:** Use the **Intel RealSense D435i** depth camera and 3D LiDAR to identify medical kits, patient posture, and injury sites.
*   **VLA Models:** Leverage **Vision-Language-Action (VLA)** models (like Unitree’s UnifoLM-VLA) to bridge the gap between "I see a wound" and "I need to apply pressure."

### Layer C: The Action Bridge (ROS2 & SDK)
*   **Unitree SDK:** Use the C++/Python SDK to send high-level commands to the motors.
*   **ROS2 (Robot Operating System 2):** Acts as the nervous system, connecting the "Medical Brain" (LLM) to the "Body" (Motors/Sensors).

---

## 3. Implementation Roadmap

### Phase 1: Knowledge Integration (Month 1-2)
*   Set up the Jetson Orin environment with **NVIDIA JetPack**.
*   Deploy a quantized LLM and create the vector database with your Paramedic protocols.
*   Test the system's ability to answer medical queries based *only* on the uploaded documents.

### Phase 2: Dexterous Training (Month 3-5)
*   Use **Unitree’s Reinforcement Learning** tools and **NVIDIA Isaac Gym**.
*   Train the robot in simulation to perform basic medical tasks: opening a kit, picking up a gauze pad, or using a stethoscope.

### Phase 3: Autonomous Protocol Execution (Month 6+)
*   Integrate the "Brain" and "Body."
*   Scenario: The robot identifies a medical emergency via its camera, retrieves the protocol, and physically initiates the first steps of care autonomously.

---

## 4. Technical Summary for Your Team
*   **Hardware:** Unitree G1 EDU Ultimate B (U4)
*   **AI Module:** NVIDIA Jetson Orin (100 TOPS)
*   **Frameworks:** ROS2, Unitree SDK, PyTorch, LangChain (for RAG).
*   **Deployment:** 100% local/offline for data privacy and reliability.

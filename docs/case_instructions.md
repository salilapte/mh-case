# Model Health: Case Study - Algorithm & Data Scientist Position

Welcome! This repository is the starting point for your case project. Below are the instructions on the data, environment setup, and the task we’d like you to complete.

At **Model Health**, we aim to empower physiotherapists and coaches with **actionable biomechanical insights**.  
Our vision is to:  
- Make it easy for practitioners to track longitudinal performance changes in their patients.  
- Enable comparisons between different athletes.  
- Present results in a clear and accessible way so that insights can be explained directly to patients/athletes.  

This case will give you a chance to work with real-world data and demonstrate how you approach extracting insights and communicating them effectively.

---

## **The Case**

You will be working on **drop vertical jumps** – a movement highly relevant to many of our clients.  

We will provide you with **raw kinematics data** from multiple drop vertical jumps performed by different athletes/patients. Your challenge is to turn this raw data into **actionable insights** for a physiotherapist or coach.  

Specifically, we want you to focus on computing the **Reactive Strength Index (RSI)**, a key performance metric. [This blog post](https://gymaware.com/reactive-strength-index-rsi-in-sports/) is helpful to understand RSI.

When turning the data into insights, think about in what different ways a coach/physiotherapist would want to look at multiple data points.

👉 What we will be looking at:
- **Robustness of your approach**: How did you handle the raw data and ensure your results are meaningful? How did you deal with potential noise/inaccuracies in the raw data?
- **Clarity of presentation**: Can a physiotherapist or coach easily understand your outputs?
- **Communication of insights**: More important than polished graphs is how well you make your case understandable.  

---

## **Step 1: Set Up Python Environment**

You’ll need a Python environment with the following dependencies (you can install more if you like):

- `numpy`
- `pickle`
- `matplotlib`
- `pandas`

### Instructions

1. Create a **conda environment**:
    ```bash
    conda create -n mh_case python=3.9 numpy pandas matplotlib
    ```
2. Activate the environment:
    ```bash
    conda activate mh_case
    ```

---

## **Step 2: Download the Kinematics Data**

### Download
- Download the kinematics data from [this link](https://drive.google.com/drive/u/0/folders/1DXYWaZd64VvoEAcBO6HapGqgJ5gbZ4Tv). 
- Copy the folder into the root directory of this repository as:  
  `MH_case/Data`

### Directory Structure

The **Data** folder contains multiple **sessions**, each collected with a single subject. Inside each session you’ll find:

- **MarkerData**
- **OpenSimData**
  - Kinematics
  - Model

#### OpenSimData/Kinematics
Each trial contains:  
- **.mot**: OpenSim format of kinematics (can be visualized in the OpenSim GUI).  
- **.pkl**: A preprocessed dictionary with:  
  - Time-series of generalized coordinates  
  - Time-series of body kinematics (Cartesian coordinates of body segments)  
  - Stored as **pandas dataframes**  

For background on the biomechanical model, see [this page](https://modelhealth.notion.site/Musculoskeletal-model-22b67c127383804d918fddf2baec47fd).

#### OpenSimData/Model
- **.osim**: OpenSim model file, scaled to the subject’s geometry. You don't need to use this file directly (see Step 4).

#### MarkerData
- **.trc**: Virtual 3D markers reconstructed from videos. Used for visualization in OpenSim. You don't need to use this file directly but you can use it to visualize markers for yourself.

---

## **Step 3: Run the Example Script**

We’ve included a small script to help you get started.

1. Run:
    ```bash
    python main.py
    ```
2. This will demonstrate how to **load** and **visualize** the data.

---

## **Step 4 (Optional): Visualize Skeletons in OpenSim (detailed)**

If you’d like to better understand the motions visually, use the OpenSim GUI. The steps below show exactly how to open the model and load the motion files.

### Download & Install OpenSim
1. Go to the [OpenSim GUI download page](https://simtk.org/frs/?group_id=91).  
2. Download and install the version for your OS (Windows or Mac). Follow the installer instructions for your system.

### Open a Model (.osim)
1. Launch **OpenSim GUI**.
2. From the top menu select **File > Open Model...**.
3. In the file dialog, navigate to `MH_case/Data/<session>/OpenSimData/Model` and choose the `.osim` file for that subject.
4. Click **Open**.  
   - The model will appear in the **Navigator** pane on the left (typically under a node named after the model or “Models”).

### Load a Motion (.mot)
You can load a motion using either of these two ways:

1. In the **Navigator** pane, find the model node you just opened (expand it if necessary).
2. **Right-click** on the model node and choose **Load Motion...** (or **Load Motion**).
3. In the file dialog, navigate to `OpenSimData/Kinematics` and select the `.mot` file for the trial you want to view.
4. Click **Open** — the motion should be loaded and the animation will appear in the visualizer.

This OpenSim GUI workflow is optional but can be very helpful to build intuition about the movements before computing metrics.

---

## **Conclusion**

Your task is to:  
- Extract and compute **RSI** from the provided trials.  
- Compare and present results across **trials and subjects**.  
- Make the output **clear, insightful, and usable** for a physiotherapist/coach.  

We don’t expect you to build a polished product in this short case. Instead, we want to see **how you think, structure your analysis, and communicate results**. You can present your results in **any format** (PowerPoint [max 10 slides], PDF [max 2 pages], Jupyter Notebook). Please send us the following materials 24 hours before your interview is scheduled:
- the results you want to present (ppt, pdf, notebook, ...)
- a zip folder with your code (no instructions needed for us, we will not run it). It serves as reference.

During the interview, we will discuss the case (there is nothing more you should prepare).


If you encounter issues with the setup or data, please contact us directly.

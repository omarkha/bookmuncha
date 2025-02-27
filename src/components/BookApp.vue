<template>
    <div class="container">
      <!-- App Explanation Section -->
      <div class="intro-section upload-section">
        <h1>Welcome to BookMuncha</h1>
        <p>
          BookMuncha is an innovative app designed to help you quickly understand the content of your books or documents. 
          Simply upload a file, and the app will break it into chunks for easy analysis. You can then ask specific 
          questions about the book, and the app will return relevant answers based on the content.
        </p>
        <p>
          Whether you're trying to grasp the key themes or searching for specific information, BookMuncha makes it 
          easy to interact with your documents. Upload any supported file type (PDF, EPUB, DOCX, or image), ask 
          a question, and get precise, context-based responses.
        </p>
  
        <!-- File Upload Section -->
        <input type="file" id="fileInput" @change="uploadFile" :disabled="isUploading" />
        
        <!-- Loading Indicator for Upload -->
        <div v-if="isUploading" class="loading-spinner">Uploading...</div>
  
        <!-- Textarea for Typing a Question -->
        <textarea v-model="userQuestion" placeholder="Type your question here..." rows="4" cols="50" :disabled="isUploading"></textarea>
  
        <!-- Slider to select the number of answers -->
        <div>
          <label for="answerCount">Number of Answers:</label>
          <input 
            type="range" 
            id="answerCount" 
            min="1" 
            max="30" 
            v-model="answerCount" 
            :disabled="isUploading || isAskingQuestion" 
          />
          <span>{{ answerCount }}</span>
        </div>
  
        <button @click="askQuestion" :disabled="isUploading || isAskingQuestion">Ask Question</button>
  
        <!-- Loading Indicator for Question -->
        <div v-if="isAskingQuestion" class="loading-spinner">Processing your question...</div>
      </div>
  
      <!-- Displaying the Answers -->
      <div v-if="answers.length" class="answers-section">
        <h2>Answers:</h2>
        <ul>
          <li v-for="(answer, index) in answers" :key="index">{{ "Page: " + answer.page_number + " \n " + answer.text }}</li>
        </ul>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    data() {
      return {
        file: null,
        answers: [],
        chunks: [],
        userQuestion: "",  // For storing the user's question
        answerCount: 5,    // Initial value for the number of answers to show
        isUploading: false, // Track uploading state
        isAskingQuestion: false // Track asking question state
      };
    },
    methods: {
      async uploadFile(event) {
        this.isUploading = true;
        try {
          this.file = event.target.files[0];
          let formData = new FormData();
          formData.append("file", this.file);
  
          let response = await axios.post("https://bookmuncha.onrender.com/api/upload", formData);
          this.chunks = response.data.chunks;
        } catch (error) {
          console.error("Error uploading file:", error);
          alert("An error occurred while uploading the file. Please try again.");
        } finally {
          this.isUploading = false;
        }
      },
      async askQuestion() {
        if (!this.userQuestion.trim()) {
          alert("Please type a question.");
          return;
        }
  
        this.isAskingQuestion = true;
        try {
          let response = await axios.post("https://bookmuncha.onrender.com/api/answer", {
            question: this.userQuestion,  // Send the user-defined question
            chunks: this.chunks,
            limit: this.answerCount  // Send the selected number of answers
          });
  
          this.answers = response.data.answers;
        } catch (error) {
          console.error("Error asking the question:", error);
          alert("An error occurred while processing your question. Please try again.");
        } finally {
          this.isAskingQuestion = false;
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .container {
    display: flex;
    flex-direction: row;
    gap: 5vw;
    max-width: 93vw;
    margin: 40px auto;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9f9f9;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  .intro-section, .upload-section {
    text-align: center;
    margin-bottom: 20px;
    width: 38vw;
    height: 76vh;
  }
  
  .intro-section h1 {
    font-size: 24px;
    color: #007bff;
  }
  
  .intro-section p {
    font-size: 16px;
    color: #333;
    line-height: 1.5;
  }
  
  .upload-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }
  
  input[type="file"] {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
  }
  
  textarea {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
    width: 100%;
    max-width: 100%;
    resize: none;
  }
  
  button {
    padding: 10px 15px;
    border: none;
    background-color: #007bff;
    color: white;
    font-size: 16px;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.3s ease;
  }
  
  button:hover {
    background-color: #0056b3;
  }
  
  .answers-section {
    margin-top: 20px;
    width: 62vw;
    max-height: 62vh;
    overflow-y: scroll;
    box-shadow: inset 0 0 5vw 1px rgba(0,0,0,0.24)
  }
  
  h2 {
    color: #333;
  }
  
  ul {
    list-style: none;
    padding: 0;
  }
  
  li {
    background: #fff;
    padding: 10px;
    margin-top: 5px;
    border-radius: 4px;
    border-left: 4px solid #007bff;
  }
  
  input[type="range"] {
    width: 80%;
    margin-top: 10px;
  }
  
  span {
    margin-left: 10px;
    font-size: 16px;
  }
  </style>
  
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ActivityIndicator,
  StyleSheet,
  TouchableOpacity,
  Modal,
  ScrollView,
} from 'react-native';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Component for displaying data
const DataTable = ({ category, question }) => {
  if (!category || !question) return null;

  const groupedData = category.responses.reduce((arr, catValue) => {
    const categoryValue = catValue.content;
    if (!arr[categoryValue]) {
      arr[categoryValue] = [];
    }
    const questionResponse = question.responses.find(q => q.id === catValue.id);
    if (questionResponse) {
      arr[categoryValue].push(questionResponse.content);
    }
    return arr;
  }, {});

  const categoryData = Object.entries(groupedData).map(([categoryValue, questionValues]) => ({
    categoryValue,
    count: questionValues.length,
    values: questionValues.sort()
  }));

  return (
    <View style={styles.tableContainer}>
      <View style={styles.tableHeader}>
        <Text style={styles.tableHeaderCell}>{category.title}</Text>
        <Text style={styles.tableHeaderCell}>Count</Text>
        <Text style={styles.tableHeaderCell}>Values</Text>
      </View>
      <ScrollView style={styles.tableBody}>
        {categoryData.map(({ categoryValue, count, values }) => (
          <View key={categoryValue} style={styles.tableRow}>
            <Text style={styles.tableCell}>{categoryValue}</Text>
            <Text style={styles.tableCell}>{count}</Text>
            <Text style={styles.tableCell}>{values.join('\n')}</Text>
          </View>
        ))}
      </ScrollView>
    </View>
  );
};

export default function App() {
  const [surveys, setSurveys] = useState([]);
  const [selectedSurvey, setSelectedSurvey] = useState(null);
  const [selectedCategory , setSelectedCategory] = useState('');
  const [selectedQuestion, setSelectedQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showSurveyPicker, setShowSurveyPicker] = useState(false);
  const [showCategoryPicker, setShowCategoryPicker] = useState(false);
  const [showQuestionPicker, setShowQuestionPicker] = useState(false);

  const fetchSurveys = async () => {
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/surveys`);
      if (response.data.status === 'success') {
        setSurveys(response.data.data.surveys);
        console.log(response.data.data.surveys);
      }
    } catch (err) {
      setError('Failed to fetch surveys');
      console.error('Error:', err);
    }
  };

  useEffect(() => {
    fetchSurveys();
  }, []);

  const handleSurveySelect = async (surveyName) => {
    setSelectedSurvey(surveys.find(survey => survey.name === surveyName));
    console.log(selectedSurvey);
    setSelectedCategory('');
    setSelectedQuestion('');
    setShowSurveyPicker(false);
    setLoading(true);
    setError(null);
    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>Survey Viewer</Text>
          <TouchableOpacity 
            style={styles.refreshButton}
            onPress={fetchSurveys}
          >
            <Text style={styles.refreshButtonText}>{'\u21BB'}</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity 
          style={styles.surveyButton}
          onPress={() => setShowSurveyPicker(true)}
        >
          <Text style={styles.surveyButtonText}>
            {selectedSurvey?.name || 'Select Survey'}
          </Text>
        </TouchableOpacity>

        {selectedSurvey?.name && selectedSurvey?.questions_or_fields && (
          <View style={styles.questionSelectors}>
            <TouchableOpacity 
              style={styles.questionButton}
              onPress={() => setShowCategoryPicker(true)}
            >
              <Text style={styles.questionButtonText}>
                {selectedCategory || 'Select Category'}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={styles.questionButton}
              onPress={() => setShowQuestionPicker(true)}
            >
              <Text style={styles.questionButtonText}>
                {selectedQuestion || 'Select Question'}
              </Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Survey Picker Modal */}
        <Modal
          visible={showSurveyPicker}
          transparent={true}
          animationType="slide"
        >
          <View style={styles.modalContainer}>
            <View style={styles.modalContent}>
              <Text style={styles.modalTitle}>Select Survey</Text>
              <ScrollView style={styles.modalScrollView}>
                {surveys.map((survey, index) => (
                  <TouchableOpacity
                    key={index}
                    style={styles.surveyOption}
                    onPress={() => handleSurveySelect(survey.name)}
                  >
                    <Text style={styles.surveyOptionText}>{survey.name}</Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setShowSurveyPicker(false)}
              >
                <Text style={styles.closeButtonText}>Close</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>

        {/* Category Picker Modal */}
        <Modal
          visible={showCategoryPicker}
          transparent={true}
          animationType="slide"
        >
          <View style={styles.modalContainer}>
            <View style={styles.modalContent}>
              <Text style={styles.modalTitle}>Select Category</Text>
              <ScrollView style={styles.modalScrollView}>
                {selectedSurvey?.questions_or_fields?.slice(0, 7).map((category) => (
                  <TouchableOpacity
                    key={category.title}
                    style={styles.surveyOption}
                    onPress={() => {
                      setSelectedCategory(category.title);
                      setShowCategoryPicker(false);
                    }}
                  >
                    <Text style={styles.surveyOptionText}>{category.title}</Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setShowCategoryPicker(false)}
              >
                <Text style={styles.closeButtonText}>Close</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>

        {/* Question Picker Modal */}
        <Modal
          visible={showQuestionPicker}
          transparent={true}
          animationType="slide"
        >
          <View style={styles.modalContainer}>
            <View style={styles.modalContent}>
              <Text style={styles.modalTitle}>Select Question</Text>
              <ScrollView style={styles.modalScrollView}>
                {selectedSurvey?.questions_or_fields?.slice(7).map((question) => (
                  <TouchableOpacity
                    key={question.title}
                    style={styles.surveyOption}
                    onPress={() => {
                      setSelectedQuestion(question.title);
                      setShowQuestionPicker(false);
                    }}
                  >
                    <Text style={styles.surveyOptionText}>{question.title}</Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setShowQuestionPicker(false)}
              >
                <Text style={styles.closeButtonText}>Close</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>

        {loading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#0000ff" />
          </View>
        )}

        {error && (
          <Text style={styles.errorText}>{error}</Text>
        )}

        {selectedCategory && selectedQuestion && (
          <View style={styles.tableSection}>
            <Text style={styles.tableTitle}>Data Comparison</Text>
            <DataTable 
              category={selectedSurvey?.questions_or_fields.find(q => q.title === selectedCategory)}
              question={selectedSurvey?.questions_or_fields.find(q => q.title === selectedQuestion)}
            />
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  refreshButton: {
    padding: 10,
    marginLeft: 10,
    marginBottom: 20,
  },
  refreshButtonText: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  surveyButton: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
  },
  surveyButtonText: {
    color: 'white',
    textAlign: 'center',
    fontSize: 16,
    fontWeight: '600',
  },
  questionSelectors: {
    marginTop: 20,
    gap: 10,
  },
  questionButton: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
  },
  questionButtonText: {
    color: 'white',
    textAlign: 'center',
    fontSize: 16,
    fontWeight: '600',
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 20,
    width: '80%',
    maxHeight: '80%',
    display: 'flex',
    flexDirection: 'column',
  },
  modalScrollView: {
    maxHeight: '70%',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'center',
  },
  surveyOption: {
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  surveyOptionText: {
    fontSize: 16,
  },
  closeButton: {
    marginTop: 15,
    padding: 15,
    backgroundColor: '#ff3b30',
    borderRadius: 8,
  },
  closeButtonText: {
    color: 'white',
    textAlign: 'center',
    fontSize: 16,
    fontWeight: '600',
  },
  loadingContainer: {
    padding: 20,
    alignItems: 'center',
  },
  errorText: {
    color: 'red',
    textAlign: 'center',
    marginVertical: 10,
  },
  tableSection: {
    marginTop: 20,
    padding: 10,
  },
  tableTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  tableContainer: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    overflow: 'hidden',
    marginTop: 20,
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#f5f5f5',
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  tableHeaderCell: {
    flex: 1,
    padding: 10,
    fontWeight: 'bold',
    textAlign: 'center',
    fontSize: 14,
  },
  tableBody: {
    maxHeight: 400,
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  tableCell: {
    flex: 1,
    padding: 10,
    textAlign: 'center',
    fontSize: 14,
  },
});

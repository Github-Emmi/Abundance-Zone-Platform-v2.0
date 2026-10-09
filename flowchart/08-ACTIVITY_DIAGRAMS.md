# 08 - Activity Diagrams

Activity diagrams show the business process workflows and user interactions for key features in Abundance Zone Platform v2.0.

---

## 1. Youth Registration Activity Diagram

```mermaid
flowchart TD
    Start([Coordinator Opens<br/>Youth Registration]) --> FillForm[Fill Registration Form]
    
    FillForm --> EnterDetails[Enter Youth Details:<br/>Name, Phone, Email, DOB,<br/>Branch, Department]
    
    EnterDetails --> UploadPhoto{Upload<br/>Profile Photo?}
    UploadPhoto -->|Yes| SelectPhoto[Select Photo<br/>from Device]
    UploadPhoto -->|No| ValidateForm
    SelectPhoto --> ValidateForm[Validate Form Fields]
    
    ValidateForm --> Valid{All Fields<br/>Valid?}
    Valid -->|No| ShowErrors[Show Validation Errors]
    ShowErrors --> FillForm
    
    Valid -->|Yes| CheckDuplicate[Check for<br/>Duplicate Youth]
    CheckDuplicate --> Duplicate{Duplicate<br/>Found?}
    
    Duplicate -->|Yes| ShowDuplicateError[Show Duplicate Error:<br/>Youth with same phone/email exists]
    ShowDuplicateError --> End1([End])
    
    Duplicate -->|No| SaveYouth[Save Youth Record<br/>to Database]
    SaveYouth --> EmitEvent[Emit YouthRegistered<br/>Domain Event]
    
    EmitEvent --> SendNotification[Send Notification<br/>to Coordinator]
    SendNotification --> CacheProfile[Cache Youth Profile<br/>in Redis]
    
    CacheProfile --> ShowSuccess[Show Success Message:<br/>Youth Registered Successfully]
    ShowSuccess --> AskAnother{Register<br/>Another Youth?}
    
    AskAnother -->|Yes| FillForm
    AskAnother -->|No| End2([End])
    
    style SaveYouth fill:#90EE90
    style ShowSuccess fill:#90EE90
```

**Business Rules:**
- Phone and email must be unique across all youths
- Age must be between 10-30 years
- Branch and department must exist
- Profile photo max size: 5MB
- Registration requires BRANCH_COORDINATOR role

---

## 2. Event Creation Activity Diagram

```mermaid
flowchart TD
    Start([Coordinator Opens<br/>Create Event]) --> EnterBasic[Enter Event Details:<br/>Name, Description, Type]
    
    EnterBasic --> SetDateTime[Set Date & Time:<br/>Start Time, End Time]
    SetDateTime --> SetLocation[Set Location:<br/>Venue, Address]
    
    SetLocation --> SelectBranch[Select Target Branch]
    SelectBranch --> SelectDept{Select Specific<br/>Department?}
    
    SelectDept -->|Yes| ChooseDept[Choose Department]
    SelectDept -->|No| AllDepts[Target All Departments]
    
    ChooseDept --> SetCapacity
    AllDepts --> SetCapacity[Set Max Capacity]
    
    SetCapacity --> AddDescription[Add Additional<br/>Instructions]
    AddDescription --> ValidateEvent[Validate Event Data]
    
    ValidateEvent --> EventValid{All Fields<br/>Valid?}
    EventValid -->|No| ShowErrors[Show Validation Errors]
    ShowErrors --> EnterBasic
    
    EventValid -->|Yes| SaveDraft{Save as<br/>Draft?}
    SaveDraft -->|Yes| SaveAsDraft[Save Event as Draft]
    SaveAsDraft --> End1([End])
    
    SaveDraft -->|No| PublishEvent[Publish Event]
    PublishEvent --> GenerateQR[Generate QR Codes:<br/>Check-in & Check-out]
    
    GenerateQR --> CreateFirestore[Create Event in<br/>Firestore]
    CreateFirestore --> ResolveYouths[Resolve Target Youths:<br/>Query by Branch/Dept]
    
    ResolveYouths --> QueueNotifications[Queue Notification Task<br/>to Celery]
    QueueNotifications --> ProcessNotif[Celery Worker Processes:<br/>Send Push + Email to Youths]
    
    ProcessNotif --> ShowSuccess[Show Success Message:<br/>Event Published Successfully]
    ShowSuccess --> DisplayQR[Display QR Codes<br/>for Printing]
    
    DisplayQR --> End2([End])
    
    style PublishEvent fill:#90EE90
    style ShowSuccess fill:#90EE90
```

**Business Rules:**
- Event start time must be in the future
- End time must be after start time
- Max capacity optional (0 = unlimited)
- QR codes valid only during event window
- Notifications sent only to youths in target branch/department
- Requires BRANCH_COORDINATOR role

---

## 3. Attendance Marking Activity Diagram (QR Code)

```mermaid
flowchart TD
    Start([Youth Opens<br/>Mobile App]) --> ViewEvents[View Upcoming Events]
    
    ViewEvents --> SelectEvent[Select Event to Attend]
    SelectEvent --> CheckEventStatus{Event<br/>Status?}
    
    CheckEventStatus -->|Not Started| ShowWaitMsg[Show: Event hasn't started yet]
    ShowWaitMsg --> End1([End])
    
    CheckEventStatus -->|In Progress| ClickCheckIn[Click Check-in Button]
    CheckEventStatus -->|Ended| ShowEndedMsg[Show: Event has ended]
    ShowEndedMsg --> End1
    
    ClickCheckIn --> OpenCamera[Open Camera<br/>for QR Scan]
    OpenCamera --> ScanQR[Scan Check-in QR Code]
    
    ScanQR --> ValidateQR[Validate QR Code]
    ValidateQR --> QRValid{QR Code<br/>Valid?}
    
    QRValid -->|No| ShowInvalidQR[Show: Invalid QR Code]
    ShowInvalidQR --> End2([End])
    
    QRValid -->|Yes| CheckExisting[Check Existing<br/>Attendance Record]
    CheckExisting --> AlreadyChecked{Already<br/>Checked In?}
    
    AlreadyChecked -->|Yes| ShowAlreadyMsg[Show: Already checked in]
    ShowAlreadyMsg --> End2
    
    AlreadyChecked -->|No| RecordCheckIn[Record Check-in:<br/>Create Attendance Record]
    RecordCheckIn --> SyncFirestore[Sync to Firestore<br/>Real-time Update]
    
    SyncFirestore --> ShowCheckInSuccess[Show Success:<br/>Checked in at HH:MM]
    ShowCheckInSuccess --> YouthAttendsEvent[Youth Attends Event...]
    
    YouthAttendsEvent --> EventEnding{Event<br/>Ending?}
    EventEnding -->|No| YouthAttendsEvent
    EventEnding -->|Yes| ClickCheckOut[Click Check-out Button]
    
    ClickCheckOut --> OpenCameraOut[Open Camera<br/>for QR Scan]
    OpenCameraOut --> ScanQROut[Scan Check-out QR Code]
    
    ScanQROut --> ValidateQROut[Validate QR Code]
    ValidateQROut --> QRValidOut{QR Code<br/>Valid?}
    
    QRValidOut -->|No| ShowInvalidQROut[Show: Invalid QR Code]
    ShowInvalidQROut --> End3([End])
    
    QRValidOut -->|Yes| RecordCheckOut[Record Check-out:<br/>Update Attendance]
    RecordCheckOut --> CalcDuration[Calculate Event Duration]
    
    CalcDuration --> CheckDuration{Duration >=<br/>Threshold?}
    CheckDuration -->|Yes| MarkPresent[Mark Status: Present]
    CheckDuration -->|No| MarkEarly[Mark Status: Early Departure]
    
    MarkPresent --> UpdateRate[Update Youth<br/>Attendance Rate]
    MarkEarly --> FlagReview[Flag for<br/>Coordinator Review]
    
    UpdateRate --> SyncFirestoreOut
    FlagReview --> SyncFirestoreOut[Sync to Firestore]
    
    SyncFirestoreOut --> InvalidateCache[Invalidate Redis Cache]
    InvalidateCache --> ShowCheckOutSuccess[Show Success:<br/>Checked out at HH:MM]
    
    ShowCheckOutSuccess --> End4([End])
    
    style RecordCheckIn fill:#FFD700
    style MarkPresent fill:#90EE90
    style UpdateRate fill:#90EE90
```

**Business Rules:**
- Check-in allowed only during event window (start_time to end_time + 30 min)
- Check-out required within 1 hour after event end
- Early departure if duration < (event_duration - 30 minutes)
- Attendance rate recalculated immediately
- Real-time sync to Firestore for coordinator dashboard

---

## 4. Bulk Attendance Marking Activity Diagram (Coordinator)

```mermaid
flowchart TD
    Start([Coordinator Opens<br/>Bulk Attendance]) --> SelectEvent[Select Event]
    
    SelectEvent --> ViewYouthList[View Youth List:<br/>All Registered Youths]
    
    ViewYouthList --> ChooseMethod{Bulk Marking<br/>Method?}
    ChooseMethod -->|Manual Selection| ManualSelect[Select Youths<br/>One by One]
    ChooseMethod -->|Select All| SelectAll[Select All Youths]
    ChooseMethod -->|Import CSV| UploadCSV[Upload CSV File]
    
    ManualSelect --> MarkStatus
    SelectAll --> MarkStatus
    UploadCSV --> ValidateCSV[Validate CSV Format]
    
    ValidateCSV --> CSVValid{CSV<br/>Valid?}
    CSVValid -->|No| ShowCSVError[Show CSV Errors]
    ShowCSVError --> UploadCSV
    CSVValid -->|Yes| MarkStatus
    
    MarkStatus[Mark Attendance Status:<br/>Present, Absent, Late]
    MarkStatus --> AddNotes{Add Notes<br/>for Absences?}
    
    AddNotes -->|Yes| EnterNotes[Enter Absence Reason]
    AddNotes -->|No| Preview
    EnterNotes --> Preview[Preview Bulk Changes]
    
    Preview --> Confirm{Confirm<br/>Changes?}
    Confirm -->|No| ViewYouthList
    Confirm -->|Yes| CheckCount{Record<br/>Count?}
    
    CheckCount -->|< 100| ProcessSync[Process Synchronously]
    CheckCount -->|>= 100| ProcessAsync[Queue Celery Task:<br/>Background Processing]
    
    ProcessSync --> SaveRecords[Save Attendance Records]
    ProcessAsync --> QueueTask[Enqueue Task to Redis]
    QueueTask --> ShowTaskID[Show Task ID:<br/>Processing in background]
    ShowTaskID --> End1([End])
    
    SaveRecords --> UpdateStatuses[Update Youth<br/>Attendance Rates]
    UpdateStatuses --> SyncFirestore[Sync to Firestore]
    SyncFirestore --> InvalidateCache[Invalidate Redis Cache]
    
    InvalidateCache --> SendNotifications[Send Notifications:<br/>Absent Youths + Parents]
    SendNotifications --> ShowSuccess[Show Success:<br/>X Records Updated]
    
    ShowSuccess --> GenerateReport[Generate Summary Report]
    GenerateReport --> End2([End])
    
    style SaveRecords fill:#FFD700
    style ShowSuccess fill:#90EE90
```

**Business Rules:**
- Max 500 records per synchronous operation
- >500 records processed asynchronously via Celery
- CSV format: youth_id, status, notes
- Notifications sent only to absent youths
- Attendance rate recalculated for all affected youths
- Requires BRANCH_COORDINATOR or DEPARTMENT_LEADER role

---

## 5. Pledge Payment Activity Diagram

```mermaid
flowchart TD
    Start([Youth Opens<br/>My Pledges]) --> ViewPledges[View Active Pledges]
    
    ViewPledges --> SelectPledge[Select Pledge<br/>to Pay]
    SelectPledge --> CheckStatus{Pledge<br/>Status?}
    
    CheckStatus -->|Fully Paid| ShowPaidMsg[Show: Already fully paid]
    ShowPaidMsg --> End1([End])
    
    CheckStatus -->|Active| EnterAmount[Enter Payment Amount]
    CheckStatus -->|Overdue| ShowOverdueWarning[Show Overdue Warning]
    ShowOverdueWarning --> EnterAmount
    
    EnterAmount --> ValidateAmount{Amount<br/>Valid?}
    ValidateAmount -->|No| ShowAmountError[Show: Invalid amount or<br/>exceeds remaining balance]
    ShowAmountError --> EnterAmount
    
    ValidateAmount -->|Yes| SelectMethod{Payment<br/>Method?}
    SelectMethod -->|Cash| ChooseCash[Cash Payment]
    SelectMethod -->|Bank Transfer| ChooseBank[Bank Transfer]
    SelectMethod -->|Mobile Money| ChooseMobile[Mobile Money]
    
    ChooseCash --> UploadReceipt
    ChooseBank --> UploadReceipt
    ChooseMobile --> UploadReceipt
    
    UploadReceipt[Upload Receipt Image]
    UploadReceipt --> TakePhoto{Take Photo<br/>or Gallery?}
    
    TakePhoto -->|Camera| CapturePhoto[Capture Receipt Photo]
    TakePhoto -->|Gallery| SelectFromGallery[Select from Gallery]
    
    CapturePhoto --> CompressImage
    SelectFromGallery --> CompressImage[Compress Image<br/>Max 2MB]
    
    CompressImage --> UploadToStorage[Upload to<br/>Cloud Storage]
    UploadToStorage --> ShowUploading[Show: Uploading receipt...]
    
    ShowUploading --> InitiateOCR[Initiate OCR Processing:<br/>Send to GPT-4o Vision]
    InitiateOCR --> ShowOCRProcessing[Show: Extracting payment details...]
    
    ShowOCRProcessing --> OCRComplete[OCR Extracts:<br/>Amount, Date, Merchant]
    OCRComplete --> ValidateOCR{Extracted<br/>Amount Matches?}
    
    ValidateOCR -->|No| ShowMismatch[Show Mismatch Warning:<br/>Manual Review Required]
    ShowMismatch --> ManualReview{Proceed<br/>Anyway?}
    ManualReview -->|No| UploadReceipt
    ManualReview -->|Yes| FlagManualReview[Flag for Manual Review]
    
    ValidateOCR -->|Yes| AutoApprove[Auto-approve Payment]
    FlagManualReview --> CreatePayment
    AutoApprove --> CreatePayment[Create Payment Record]
    
    CreatePayment --> UpdatePledge[Update Pledge Progress]
    UpdatePledge --> CheckComplete{Pledge<br/>Fully Paid?}
    
    CheckComplete -->|Yes| MarkFullyPaid[Mark Pledge: Fully Paid]
    CheckComplete -->|No| MarkPartial[Mark Pledge: Partially Paid]
    
    MarkFullyPaid --> CancelReminders[Cancel Scheduled Reminders]
    MarkPartial --> UpdateReminders[Update Reminder Schedule]
    
    CancelReminders --> NotifySuccess
    UpdateReminders --> NotifySuccess[Send Confirmation<br/>Notification]
    
    NotifySuccess --> ShowPaymentSuccess[Show Success:<br/>Payment recorded successfully]
    ShowPaymentSuccess --> DisplayReceipt[Display Payment Receipt]
    
    DisplayReceipt --> End2([End])
    
    style CreatePayment fill:#DDA0DD
    style MarkFullyPaid fill:#90EE90
    style ShowPaymentSuccess fill:#90EE90
```

**Business Rules:**
- Payment amount cannot exceed remaining balance
- Receipt image required for all payments
- OCR extraction triggers automatic approval if amount matches
- Manual review required if OCR amount ≠ entered amount
- Reminders canceled when pledge fully paid
- Confirmation notification sent to youth

---

## 6. AI Chat Assistant Activity Diagram

```mermaid
flowchart TD
    Start([User Opens<br/>AI Assistant]) --> LoadHistory[Load Chat History<br/>from Cache]
    
    LoadHistory --> DisplayChat[Display Previous<br/>Conversations]
    DisplayChat --> EnterMessage[User Enters Message]
    
    EnterMessage --> ShowTyping[Show: AI is thinking...]
    ShowTyping --> BuildContext[Build Context:<br/>User role, Branch, Recent data]
    
    BuildContext --> CheckCache{Similar Query<br/>in Cache?}
    CheckCache -->|Yes| ReturnCached[Return Cached Response]
    CheckCache -->|No| CallGemini[Call Gemini API]
    
    CallGemini --> GeminiResponse{Gemini<br/>Success?}
    GeminiResponse -->|No| TryFallback[Try OpenRouter Fallback]
    TryFallback --> FallbackSuccess{Fallback<br/>Success?}
    
    FallbackSuccess -->|No| ShowError[Show: AI unavailable,<br/>please try again]
    ShowError --> End1([End])
    
    GeminiResponse -->|Yes| ParseResponse
    FallbackSuccess -->|Yes| ParseResponse[Parse AI Response]
    ReturnCached --> ParseResponse
    
    ParseResponse --> CheckAction{Response<br/>Contains Action?}
    CheckAction -->|No| DisplayResponse[Display AI Response]
    CheckAction -->|Yes| ExecuteAction[Execute Action:<br/>Query data, Generate report]
    
    ExecuteAction --> DisplayResponse
    DisplayResponse --> CacheResponse[Cache Response<br/>5 min TTL]
    
    CacheResponse --> ShowResponse[Show AI Response<br/>with Sources]
    ShowResponse --> UserReacts{User<br/>Action?}
    
    UserReacts -->|New Message| EnterMessage
    UserReacts -->|Copy Response| CopyToClipboard[Copy to Clipboard]
    UserReacts -->|Share| ShareResponse[Share Response]
    UserReacts -->|End Chat| End2([End])
    
    CopyToClipboard --> End2
    ShareResponse --> End2
    
    style CallGemini fill:#98FB98
    style DisplayResponse fill:#90EE90
```

**Business Rules:**
- Context limited to user's role and branch (RBAC)
- Responses cached for 5 minutes (same query)
- Fallback to OpenRouter if Gemini fails
- Max 10 messages in context window
- Sources cited for data-driven answers
- Rate limit: 20 queries per hour per user

---

## 7. Financial Report Generation Activity Diagram

```mermaid
flowchart TD
    Start([Coordinator Opens<br/>Financial Reports]) --> SelectReport{Report<br/>Type?}
    
    SelectReport -->|Pledge Summary| PledgeReport[Pledge Summary Report]
    SelectReport -->|Payment History| PaymentReport[Payment History Report]
    SelectReport -->|Youth Financial Status| YouthFinReport[Youth Financial Report]
    SelectReport -->|Custom Report| CustomReport[Custom Report Builder]
    
    PledgeReport --> SelectFilters
    PaymentReport --> SelectFilters
    YouthFinReport --> SelectFilters
    CustomReport --> SelectFilters
    
    SelectFilters[Select Filters:<br/>Date Range, Branch, Department]
    SelectFilters --> PreviewFilters[Preview Filter Criteria]
    
    PreviewFilters --> Confirm{Confirm<br/>Filters?}
    Confirm -->|No| SelectFilters
    Confirm -->|Yes| CheckComplexity{Report<br/>Complexity?}
    
    CheckComplexity -->|Simple| GenerateSync[Generate Synchronously]
    CheckComplexity -->|Complex| GenerateAsync[Queue Celery Task:<br/>Background Generation]
    
    GenerateSync --> QueryDatabase[Query Financial Data<br/>from PostgreSQL]
    GenerateAsync --> QueueTask[Enqueue Report Task]
    QueueTask --> NotifyWhenDone[Notify when report ready]
    NotifyWhenDone --> End1([End])
    
    QueryDatabase --> AggregatePledges[Aggregate Pledges:<br/>Total, Paid, Pending, Overdue]
    AggregatePledges --> AggregatePayments[Aggregate Payments:<br/>Methods, Amounts, Dates]
    
    AggregatePayments --> CalculateMetrics[Calculate Metrics:<br/>Collection rate, Avg payment, etc.]
    CalculateMetrics --> FormatReport[Format Report:<br/>Tables, Charts, Summary]
    
    FormatReport --> GeneratePDF[Generate PDF Document]
    GeneratePDF --> CacheReport[Cache Report<br/>1 hour TTL]
    
    CacheReport --> DisplayReport[Display Report Preview]
    DisplayReport --> UserAction{User<br/>Action?}
    
    UserAction -->|Download PDF| DownloadPDF[Download PDF File]
    UserAction -->|Export Excel| ExportExcel[Export to Excel]
    UserAction -->|Email Report| EmailReport[Email Report to Recipients]
    UserAction -->|Share Link| ShareLink[Generate Shareable Link]
    
    DownloadPDF --> End2([End])
    ExportExcel --> End2
    EmailReport --> SendEmail[Send via Email Service]
    SendEmail --> End2
    ShareLink --> CreateLink[Create Secure Link<br/>24-hour expiry]
    CreateLink --> End2
    
    style QueryDatabase fill:#DDA0DD
    style DisplayReport fill:#90EE90
```

**Business Rules:**
- Reports cached for 1 hour (same filters)
- Complex reports (>1000 records) processed asynchronously
- PDF and Excel export formats supported
- Shareable links expire after 24 hours
- Email reports as PDF attachments
- Requires BRANCH_COORDINATOR or SUPER_ADMIN role

---

## Activity Diagram Summary

### Key Business Processes

1. **Youth Registration**: Coordinator registers new youth with profile validation and duplicate checking
2. **Event Creation**: Coordinator creates events with QR code generation and automated notifications
3. **Attendance Marking (QR)**: Youth checks in/out via mobile app QR scanning with real-time sync
4. **Bulk Attendance**: Coordinator marks attendance for multiple youths with async processing for large batches
5. **Pledge Payment**: Youth records payments with receipt OCR and automatic pledge status updates
6. **AI Chat Assistant**: Users interact with AI for insights with context-aware responses and fallback handling
7. **Financial Reports**: Coordinator generates financial reports with flexible filters and multiple export formats

### Activity Diagram Characteristics

- **Swimlanes**: Multi-role activities show user vs system lanes
- **Decision Points**: Business logic expressed as diamond-shaped decisions
- **Parallel Activities**: Concurrent operations shown with fork/join nodes
- **Error Handling**: Alternative flows for validation failures and exceptions
- **System Integration**: External service calls (Firebase, Gemini, OpenAI) highlighted
- **User Experience**: Clear success/error messages and confirmation steps

### Performance Considerations

- **Async Processing**: Heavy operations queued to Celery (bulk attendance, reports, OCR)
- **Caching**: Frequent queries cached in Redis (chat responses, reports)
- **Real-time Sync**: Critical data synced to Firestore (attendance, events)
- **Batch Operations**: Bulk attendance processes 500 records per batch
- **Rate Limiting**: AI chat limited to 20 queries/hour per user

---

*Reference: Based on v1.0 business process flows and user interaction patterns*

<?xml version="1.0" ?>
<map version="0.9.0">
  <node TEXT="Patient + Documents">
    <node TEXT="Raw Documents">
      <node TEXT="Medical tests"/>
      <node TEXT="Medical letters"/>
      <node TEXT="Imaging (CT, MRI, X-ray)"/>
      <node TEXT="Other clinical documents"/>
      <node TEXT="Manually entered into Platform X"/>
    </node>
    <node TEXT="Platform X">
      <node TEXT="Patient profile">
        <node TEXT="Demographic data"/>
        <node TEXT="Main diagnosis"/>
        <node TEXT="Relevant data extracted from documents"/>
      </node>
      <node TEXT="Service history">
        <node TEXT="Previous consultations"/>
        <node TEXT="Therapies/exercises performed"/>
        <node TEXT="Patient feedback"/>
        <node TEXT="Sensor data (pulse, BP, steps)"/>
      </node>
    </node>
    <node TEXT="vCare API">
      <node TEXT="Receives profile + history from Platform X"/>
      <node TEXT="Maps disease → clinical pathway"/>
      <node TEXT="Adjusts pathway according to progress"/>
    </node>
    <node TEXT="Output to patient/doctor">
      <node TEXT="Recommended exercises"/>
      <node TEXT="Medication/monitoring reminders"/>
      <node TEXT="Critical threshold alerts"/>
      <node TEXT="Progress reports to doctor"/>
    </node>
  </node>
</map>

# SARIF to Wiz Field Mapping - Visual Reference

## Overview Diagram

```mermaid
graph LR
    SARIF["SARIF Input"]
    ENGINE["Mapping Engine"]
    TX["Transformations"]
    WIZ["Wiz Output"]
    
    SARIF -->|Extract Fields| ENGINE
    ENGINE -->|Apply Rules| TX
    TX -->|Transform Values| ENGINE
    ENGINE -->|Build Output| WIZ
    
    style SARIF fill:#e1f5ff
    style ENGINE fill:#fff3e0
    style TX fill:#ffe0b2
    style WIZ fill:#f3e5f5
```

---

## Finding Level Mappings

```mermaid
graph TD
    subgraph INPUT["SARIF Input Fields"]
        A1["ruleId"]
        A2["message.text"]
        A3["level"]
        A4["Constant"]
    end
    
    subgraph TRANSFORM["Transformation"]
        T1["map_severity:<br/>warning → Medium"]
    end
    
    subgraph OUTPUT["Wiz Output"]
        O1["name"]
        O2["description"]
        O3["severity"]
        O4["externalDetectionSource"]
        O5["id"]
    end
    
    A1 -->|Direct| O1
    A1 -->|Direct| O5
    A2 -->|Direct| O2
    A3 -->|Transform| T1
    T1 -->|Output| O3
    A4 -->|'ThirdPartyAgent'| O4
    
    style INPUT fill:#e1f5ff
    style TRANSFORM fill:#ffe0b2
    style OUTPUT fill:#f3e5f5
    style T1 fill:#ffcc80
```

| Wiz Field | Source | SARIF Path | Transform | Enabled | Default |
|-----------|--------|-----------|-----------|---------|---------|
| `name` | SARIF | `ruleId` | - | ✅ | `unnamed-finding` |
| `description` | SARIF | `message.text` | - | ✅ | `""` |
| `severity` | SARIF | `level` | `map_severity` | ✅ | `Medium` |
| `id` | SARIF | `ruleId` | - | ✅ | - |
| `externalDetectionSource` | Constant | `ThirdPartyAgent` | - | ✅ | - |

---

## Target Component Mappings

```mermaid
graph TD
    subgraph INPUT["SARIF Input"]
        B1["locations[0].physicalLocation<br/>.artifactLocation.uri"]
        B2["properties.fixedVersion"]
    end
    
    subgraph TRANSFORM["Transformations"]
        T2["clean_fixed_version:<br/>'no fix available' → ''"]
    end
    
    subgraph OUTPUT["Wiz Output"]
        O6["targetComponent.library"]
        O7["targetComponent.library.filePath"]
        O8["targetComponent.library.name"]
        O9["targetComponent.library.fixedVersion"]
    end
    
    B1 -->|Direct| O7
    B1 -->|Direct| O8
    B2 -->|Transform| T2
    T2 -->|Output| O9
    O7 --> O6
    O8 --> O6
    O9 --> O6
    
    style INPUT fill:#e1f5ff
    style TRANSFORM fill:#ffe0b2
    style OUTPUT fill:#f3e5f5
    style T2 fill:#ffcc80
```

| Wiz Field | Source | SARIF Path | Transform | Enabled |
|-----------|--------|-----------|-----------|---------|
| `targetComponent.library.filePath` | SARIF | `locations[0].physicalLocation.artifactLocation.uri` | - | ✅ |
| `targetComponent.library.name` | SARIF | `locations[0].physicalLocation.artifactLocation.uri` | - | ✅ |
| `targetComponent.library.fixedVersion` | SARIF | `properties.fixedVersion` | `clean_fixed_version` | ✅ |

---

## Optional Fields (Disabled by Default)

```mermaid
graph TD
    subgraph INPUT["SARIF Input"]
        C1["properties.fixedVersion"]
        C2["properties.cweId"]
        C3["properties.cvssScore"]
    end
    
    subgraph TRANSFORM["Transformations"]
        T3["format_remediation:<br/>'X' → 'Update to: X'"]
    end
    
    subgraph OUTPUT["Wiz Output (Disabled)"]
        O10["remediation"]
        O11["cweId"]
        O12["cvssScore"]
    end
    
    C1 -.->|Transform| T3
    T3 -.->|Disabled| O10
    C2 -.->|Disabled| O11
    C3 -.->|Disabled| O12
    
    style INPUT fill:#e1f5ff
    style TRANSFORM fill:#ffe0b2
    style OUTPUT fill:#ffebee
    style T3 fill:#ffcc80
    linkStyle 0,1,2,3,4 stroke:#999,stroke-dasharray: 5 5
```

| Wiz Field | Source | SARIF Path | Transform | Enabled |
|-----------|--------|-----------|-----------|---------|
| `remediation` | SARIF | `properties.fixedVersion` | `format_remediation` | ❌ |
| `cweId` | SARIF | `properties.cweId` | - | ❌ |
| `cvssScore` | SARIF | `properties.cvssScore` | - | ❌ |

---

## Transformations Reference

### 1. map_severity

Converts SARIF severity levels to Wiz severity levels:

```mermaid
graph LR
    A["none"] -->|Transform| B["None"]
    C["note"] -->|Transform| D["Low"]
    E["warning"] -->|Transform| F["Medium"]
    G["error"] -->|Transform| H["High"]
    
    style A fill:#e1f5ff
    style C fill:#e1f5ff
    style E fill:#e1f5ff
    style G fill:#e1f5ff
    style B fill:#f3e5f5
    style D fill:#f3e5f5
    style F fill:#f3e5f5
    style H fill:#f3e5f5
```

| Input | Output |
|-------|--------|
| `none` | `None` |
| `note` | `Low` |
| `warning` | `Medium` |
| `error` | `High` |

### 2. clean_fixed_version

Cleans fixed version field:
- If value = `"no fix available"` → returns `""`
- Otherwise → returns value as-is

### 3. format_remediation

Formats fixed version into remediation guidance:
- Template: `"Update to version: {value}"`
- Example: `"2.6.7"` → `"Update to version: 2.6.7"`

---

## Complete Data Flow

```mermaid
graph TD
    SR["SARIF Result"]
    
    subgraph MAPPING["Mapping Process"]
        M1["Extract ruleId"]
        M2["Extract message.text"]
        M3["Extract level"]
        M4["Extract URI"]
        M5["Extract fixedVersion"]
        T1["Apply Transformations"]
    end
    
    subgraph OUTPUT["Build Output"]
        O["Wiz Finding Object"]
    end
    
    SR -->|1. Parse| M1
    SR -->|2. Parse| M2
    SR -->|3. Parse| M3
    SR -->|4. Parse| M4
    SR -->|5. Parse| M5
    
    M1 -->|name, id| T1
    M2 -->|description| T1
    M3 -->|severity| T1
    M4 -->|targetComponent| T1
    M5 -->|fixedVersion| T1
    
    T1 -->|6. Build| O
    O -->|7. Validate| SR
    
    style SR fill:#e1f5ff
    style MAPPING fill:#fff3e0
    style OUTPUT fill:#f3e5f5
    style T1 fill:#ffe0b2
```

---

## Usage in LucidChart

### Steps to Import:

1. **Copy the Mermaid code** from any diagram above
2. **In LucidChart:**
   - Create new document
   - Select "Insert" → "Media"
   - Choose "Mermaid" or use the Mermaid integration
   - Paste the diagram code
3. **Customize:**
   - Adjust colors and styling as needed
   - Add notes and annotations
   - Resize and position elements
   - Export as needed

### Alternative: Create Manually

Use the tables above as reference to create custom shapes:

- **Blue boxes** = SARIF Input
- **Orange boxes** = Transformations
- **Purple boxes** = Wiz Output
- **Dashed lines** = Disabled/Optional
- **Solid lines** = Enabled/Required

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Enabled by default |
| ❌ | Disabled by default |
| → | Direct mapping |
| -.-> | Optional/disabled mapping |
| Blue | SARIF input source |
| Orange | Transformation step |
| Purple | Wiz output field |


"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Trash2, Plus, Download } from "lucide-react"

interface Attribute {
  id: string
  name: string
  type: string
  visibility: "public" | "private" | "protected"
}

interface Operation {
  id: string
  name: string
  visibility: "public" | "private" | "protected"
}

interface Connection {
  id: string
  targetClass: string
  relationship: "inheritance" | "association" | "aggregation" | "composition" | "dependency"
}

interface Note {
  id: string
  text: string
  type: "Standard" | "Information" | "Warning" | "Success" | "Confirmation" | "Decorative"
}

interface UMLClass {
  id: string
  name: string
  notes: Note[]
  attributes: Attribute[]
  operations: Operation[]
  connections: Connection[]
}

export default function UMLDiagramBuilder() {
  const [classes, setClasses] = useState<UMLClass[]>([
    {
      id: "1",
      name: "Example Class",
      notes: [],
      attributes: [{ id: "1", name: "name", type: "string", visibility: "private" }],
      operations: [{ id: "1", name: "getName()", visibility: "public" }],
      connections: [],
    },
  ])

  const [boxThickness, setBoxThickness] = useState(2)
  const [boxColor, setBoxColor] = useState("#3b82f6")

  const addNewClass = () => {
    const newClass: UMLClass = {
      id: Date.now().toString(),
      name: "New Class",
      notes: [],
      attributes: [],
      operations: [],
      connections: [],
    }
    setClasses([...classes, newClass])
  }

  const updateClassName = (classId: string, name: string) => {
    setClasses(classes.map((cls) => (cls.id === classId ? { ...cls, name } : cls)))
  }

  const addNote = (classId: string) => {
    const newNote: Note = {
      id: Date.now().toString(),
      text: "",
      type: "Standard",
    }
    setClasses(classes.map((cls) => (cls.id === classId ? { ...cls, notes: [...cls.notes, newNote] } : cls)))
  }

  const updateNote = (classId: string, noteId: string, field: keyof Note, value: string) => {
    setClasses(
      classes.map((cls) =>
        cls.id === classId
          ? {
              ...cls,
              notes: cls.notes.map((note) => (note.id === noteId ? { ...note, [field]: value } : note)),
            }
          : cls,
      ),
    )
  }

  const removeNote = (classId: string, noteId: string) => {
    setClasses(
      classes.map((cls) =>
        cls.id === classId ? { ...cls, notes: cls.notes.filter((note) => note.id !== noteId) } : cls,
      ),
    )
  }

  const addAttribute = (classId: string) => {
    const newAttribute: Attribute = {
      id: Date.now().toString(),
      name: "newAttribute",
      type: "string",
      visibility: "private",
    }
    setClasses(
      classes.map((cls) => (cls.id === classId ? { ...cls, attributes: [...cls.attributes, newAttribute] } : cls)),
    )
  }

  const updateAttribute = (classId: string, attributeId: string, field: keyof Attribute, value: string) => {
    setClasses(
      classes.map((cls) =>
        cls.id === classId
          ? {
              ...cls,
              attributes: cls.attributes.map((attr) => (attr.id === attributeId ? { ...attr, [field]: value } : attr)),
            }
          : cls,
      ),
    )
  }

  const removeAttribute = (classId: string, attributeId: string) => {
    setClasses(
      classes.map((cls) =>
        cls.id === classId ? { ...cls, attributes: cls.attributes.filter((attr) => attr.id !== attributeId) } : cls,
      ),
    )
  }

  const addOperation = (classId: string) => {
    const newOperation: Operation = {
      id: Date.now().toString(),
      name: "newOperation()",
      visibility: "public",
    }
    setClasses(
      classes.map((cls) => (cls.id === classId ? { ...cls, operations: [...cls.operations, newOperation] } : cls)),
    )
  }

  const updateOperation = (classId: string, operationId: string, field: keyof Operation, value: string) => {
    setClasses(
      classes.map((cls) =>
        cls.id === classId
          ? {
              ...cls,
              operations: cls.operations.map((op) => (op.id === operationId ? { ...op, [field]: value } : op)),
            }
          : cls,
      ),
    )
  }

  const removeOperation = (classId: string, operationId: string) => {
    setClasses(
      classes.map((cls) =>
        cls.id === classId ? { ...cls, operations: cls.operations.filter((op) => op.id !== operationId) } : cls,
      ),
    )
  }

  const addConnection = (classId: string) => {
    const newConnection: Connection = {
      id: Date.now().toString(),
      targetClass: "",
      relationship: "association",
    }
    setClasses(
      classes.map((cls) => (cls.id === classId ? { ...cls, connections: [...cls.connections, newConnection] } : cls)),
    )
  }

  const updateConnection = (classId: string, connectionId: string, field: keyof Connection, value: string) => {
    setClasses(
      classes.map((cls) =>
        cls.id === classId
          ? {
              ...cls,
              connections: cls.connections.map((conn) =>
                conn.id === connectionId ? { ...conn, [field]: value } : conn,
              ),
            }
          : cls,
      ),
    )
  }

  const removeConnection = (classId: string, connectionId: string) => {
    setClasses(
      classes.map((cls) =>
        cls.id === classId ? { ...cls, connections: cls.connections.filter((conn) => conn.id !== connectionId) } : cls,
      ),
    )
  }

  const removeClass = (classId: string) => {
    setClasses(classes.filter((cls) => cls.id !== classId))
  }

  const exportUML = () => {
    let umlText = "@startuml\n"

    classes.forEach((cls) => {
      umlText += `class ${cls.name} {\n`

      cls.notes.forEach((note) => {
        if (note.text.trim()) {
          umlText += `  note [${note.type}]: ${note.text}\n`
        }
      })

      if (cls.notes.length > 0 && (cls.attributes.length > 0 || cls.operations.length > 0)) {
        umlText += "  --\n"
      }

      cls.attributes.forEach((attr) => {
        const visibilitySymbol = attr.visibility === "public" ? "+" : attr.visibility === "private" ? "-" : "#"
        umlText += `  ${visibilitySymbol}${attr.name}: ${attr.type}\n`
      })

      if (cls.attributes.length > 0 && cls.operations.length > 0) {
        umlText += "  --\n"
      }

      cls.operations.forEach((op) => {
        const visibilitySymbol = op.visibility === "public" ? "+" : op.visibility === "private" ? "-" : "#"
        umlText += `  ${visibilitySymbol}${op.name}\n`
      })

      umlText += "}\n\n"
    })

    classes.forEach((cls) => {
      cls.connections.forEach((conn) => {
        if (conn.targetClass) {
          const relationshipSymbol = {
            inheritance: "<|--",
            association: "--",
            aggregation: "o--",
            composition: "*--",
            dependency: "..>",
          }[conn.relationship]
          umlText += `${cls.name} ${relationshipSymbol} ${conn.targetClass}\n`
        }
      })
    })

    umlText += "@enduml"

    const blob = new Blob([umlText], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "uml-diagram.puml"
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const getVisibilitySymbol = (visibility: string) => {
    switch (visibility) {
      case "public":
        return "+"
      case "private":
        return "-"
      case "protected":
        return "#"
      default:
        return "+"
    }
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">UML Diagram Builder</h1>
          <p className="text-muted-foreground">Create and export UML class diagrams with ease</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Table Section */}
          <div className="lg:col-span-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Class Definitions</CardTitle>
                <div className="flex gap-2">
                  <Button onClick={addNewClass} size="sm">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Class
                  </Button>
                  <Button onClick={exportUML} variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Export UML
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {classes.map((cls) => (
                    <div key={cls.id} className="border rounded-lg p-4 space-y-4">
                      <div className="flex items-center justify-between">
                        <Input
                          value={cls.name}
                          onChange={(e) => updateClassName(cls.id, e.target.value)}
                          className="text-lg font-semibold max-w-xs"
                          placeholder="Class Name"
                        />
                        <Button onClick={() => removeClass(cls.id)} variant="destructive" size="sm">
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>

                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <label className="text-sm font-medium text-muted-foreground">NOTES</label>
                          <Button onClick={() => addNote(cls.id)} variant="outline" size="sm">
                            <Plus className="w-3 h-3 mr-1" />
                            Add
                          </Button>
                        </div>
                        <div className="space-y-2">
                          {cls.notes.map((note) => (
                            <div key={note.id} className="flex gap-2">
                              <Input
                                value={note.text}
                                onChange={(e) => updateNote(cls.id, note.id, "text", e.target.value)}
                                placeholder="Add a note for this class..."
                                className="flex-1"
                              />
                              <Select
                                value={note.type}
                                onValueChange={(value: Note["type"]) => updateNote(cls.id, note.id, "type", value)}
                              >
                                <SelectTrigger className="w-40">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="Standard">Standard</SelectItem>
                                  <SelectItem value="Information">Information</SelectItem>
                                  <SelectItem value="Warning">Warning</SelectItem>
                                  <SelectItem value="Success">Success</SelectItem>
                                  <SelectItem value="Confirmation">Confirmation</SelectItem>
                                  <SelectItem value="Decorative">Decorative</SelectItem>
                                </SelectContent>
                              </Select>
                              <Button onClick={() => removeNote(cls.id, note.id)} variant="ghost" size="sm">
                                <Trash2 className="w-3 h-3" />
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Attributes Section */}
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-sm text-muted-foreground">ATTRIBUTES</h4>
                          <Button onClick={() => addAttribute(cls.id)} variant="outline" size="sm">
                            <Plus className="w-3 h-3 mr-1" />
                            Add
                          </Button>
                        </div>
                        <div className="space-y-2">
                          {cls.attributes.map((attr) => (
                            <div key={attr.id} className="flex items-center gap-2">
                              <Select
                                value={attr.visibility}
                                onValueChange={(value: "public" | "private" | "protected") =>
                                  updateAttribute(cls.id, attr.id, "visibility", value)
                                }
                              >
                                <SelectTrigger className="w-24">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="public">Public</SelectItem>
                                  <SelectItem value="private">Private</SelectItem>
                                  <SelectItem value="protected">Protected</SelectItem>
                                </SelectContent>
                              </Select>
                              <Input
                                value={attr.name}
                                onChange={(e) => updateAttribute(cls.id, attr.id, "name", e.target.value)}
                                placeholder="Attribute name"
                                className="flex-1"
                              />
                              <Input
                                value={attr.type}
                                onChange={(e) => updateAttribute(cls.id, attr.id, "type", e.target.value)}
                                placeholder="Type"
                                className="w-24"
                              />
                              <Button onClick={() => removeAttribute(cls.id, attr.id)} variant="ghost" size="sm">
                                <Trash2 className="w-3 h-3" />
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Operations Section */}
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-sm text-muted-foreground">OPERATIONS</h4>
                          <Button onClick={() => addOperation(cls.id)} variant="outline" size="sm">
                            <Plus className="w-3 h-3 mr-1" />
                            Add
                          </Button>
                        </div>
                        <div className="space-y-2">
                          {cls.operations.map((operation) => (
                            <div key={operation.id} className="flex items-center gap-2">
                              <Select
                                value={operation.visibility}
                                onValueChange={(value: "public" | "private" | "protected") =>
                                  updateOperation(cls.id, operation.id, "visibility", value)
                                }
                              >
                                <SelectTrigger className="w-24">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="public">Public</SelectItem>
                                  <SelectItem value="private">Private</SelectItem>
                                  <SelectItem value="protected">Protected</SelectItem>
                                </SelectContent>
                              </Select>
                              <Input
                                value={operation.name}
                                onChange={(e) => updateOperation(cls.id, operation.id, "name", e.target.value)}
                                placeholder="Operation name"
                                className="flex-1"
                              />
                              <Button onClick={() => removeOperation(cls.id, operation.id)} variant="ghost" size="sm">
                                <Trash2 className="w-3 h-3" />
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-sm text-muted-foreground">CONNECTIONS</h4>
                          <Button onClick={() => addConnection(cls.id)} variant="outline" size="sm">
                            <Plus className="w-3 h-3 mr-1" />
                            Add
                          </Button>
                        </div>
                        <div className="space-y-2">
                          {cls.connections.map((connection) => (
                            <div key={connection.id} className="flex items-center gap-2">
                              <Select
                                value={connection.targetClass}
                                onValueChange={(value) => updateConnection(cls.id, connection.id, "targetClass", value)}
                              >
                                <SelectTrigger className="flex-1">
                                  <SelectValue placeholder="Select target class" />
                                </SelectTrigger>
                                <SelectContent>
                                  {classes
                                    .filter((c) => c.id !== cls.id)
                                    .map((targetClass) => (
                                      <SelectItem key={targetClass.id} value={targetClass.name}>
                                        {targetClass.name}
                                      </SelectItem>
                                    ))}
                                </SelectContent>
                              </Select>
                              <Select
                                value={connection.relationship}
                                onValueChange={(value: Connection["relationship"]) =>
                                  updateConnection(cls.id, connection.id, "relationship", value)
                                }
                              >
                                <SelectTrigger className="w-32">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="inheritance">Inheritance</SelectItem>
                                  <SelectItem value="association">Association</SelectItem>
                                  <SelectItem value="aggregation">Aggregation</SelectItem>
                                  <SelectItem value="composition">Composition</SelectItem>
                                  <SelectItem value="dependency">Dependency</SelectItem>
                                </SelectContent>
                              </Select>
                              <Button onClick={() => removeConnection(cls.id, connection.id)} variant="ghost" size="sm">
                                <Trash2 className="w-3 h-3" />
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Styling Controls */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Styling Options</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Box Thickness</label>
                  <input
                    type="range"
                    min="1"
                    max="5"
                    value={boxThickness}
                    onChange={(e) => setBoxThickness(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="text-xs text-muted-foreground mt-1">{boxThickness}px</div>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Box Color</label>
                  <Select value={boxColor} onValueChange={setBoxColor}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="#3b82f6">Blue</SelectItem>
                      <SelectItem value="#ef4444">Red</SelectItem>
                      <SelectItem value="#10b981">Green</SelectItem>
                      <SelectItem value="#f59e0b">Orange</SelectItem>
                      <SelectItem value="#8b5cf6">Purple</SelectItem>
                      <SelectItem value="#6b7280">Gray</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Sample Box */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Preview</label>
                  {/* TODO: make a uml table box preview */}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

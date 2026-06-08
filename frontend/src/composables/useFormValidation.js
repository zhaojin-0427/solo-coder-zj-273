import { ref, reactive } from 'vue'

export function useFormValidation(getInitialForm, rules) {
  const formRef = ref(null)
  const form = reactive(getInitialForm ? getInitialForm() : {})

  const resetForm = () => {
    formRef.value?.resetFields()
    if (getInitialForm) {
      Object.assign(form, getInitialForm())
    }
  }

  const validateForm = () => {
    return new Promise((resolve) => {
      if (!formRef.value) {
        resolve(false)
        return
      }
      formRef.value.validate((valid) => {
        resolve(valid)
      })
    })
  }

  const setFormValues = (values) => {
    if (values) {
      Object.assign(form, values)
    }
  }

  return { form, formRef, resetForm, validateForm, setFormValues }
}

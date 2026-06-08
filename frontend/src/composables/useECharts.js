import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

export function useECharts(chartRef, getOption, deps = []) {
  const chart = ref(null)

  const setOption = () => {
    if (chart.value && getOption) {
      chart.value.setOption(getOption(), true)
    }
  }

  const resize = () => {
    chart.value?.resize()
  }

  const dispose = () => {
    chart.value?.dispose()
    chart.value = null
  }

  const handleResize = () => {
    resize()
  }

  onMounted(() => {
    nextTick(() => {
      if (chartRef.value) {
        chart.value = echarts.init(chartRef.value)
        setOption()
        window.addEventListener('resize', handleResize)
      }
    })
  })

  if (deps.length > 0) {
    watch(deps, () => {
      nextTick(setOption)
    }, { deep: true })
  }

  onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize)
    dispose()
  })

  return { chart, setOption, resize, dispose }
}
